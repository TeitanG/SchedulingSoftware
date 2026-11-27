Contexto del proyecto: SchedulingSoftware (backend)

    Documento para retomar el trabajo en una conversación nueva o para que alguien nuevo entienda el proyecto. Última actualización: 2026-11-27. Las decisiones de diseño y su motivo están en docs/DECISIONS.md.

1. Qué es

Software de agendamiento de citas (negocios, proveedores, servicios, horarios y citas). Es un proyecto de aprendizaje con objetivo de convertirse en producto (modelo de negocio: licencia vitalicia + cuota de mantenimiento). El backend se migró de MongoDB a PostgreSQL. El frontend (React + TypeScript + Vite) todavía no se ha empezado.
2. Stack y versiones
Pieza	Versión / detalle
Python	3.13 (venv en backend/venv)
FastAPI	Endpoints síncronos (def, no async def) porque la sesión de SQLModel es síncrona
SQLModel	0.0.49
SQLAlchemy	2.1.8
Driver	psycopg[binary] (psycopg 3)
Migraciones	Alembic
Config	pydantic-settings (App/config.py, lee .env)
Base de datos	PostgreSQL 17 en Docker (docker-compose.yml en la raíz del repo)
Docs de la API	Scalar en /scalar
Calidad	Ruff (lint/format) y Pyright (tipos)

.env (en backend/, no se sube a Git):

DATABASE_URL=postgresql+psycopg://app:app@localhost:5433/scheduling
SQL_ECHO=true
SECRET_KEY=<generar con secrets.token_urlsafe(); nunca en Git>
ACCESS_TOKEN_EXPIRE_MINUTES=10

La plantilla está en backend/.env.example. La app no arranca si faltan DATABASE_URL o SECRET_KEY.

El puerto es 5433 porque el 5432 daba problemas en Windows (probablemente otro Postgres local).
3. Estructura

backend/
├── main.py
├── alembic.ini / alembic/            ← migraciones (env.py usa get_settings y SQLModel.metadata)
├── scripts/print_ddl.py              ← imprime el CREATE TABLE / CREATE INDEX de todos los modelos
└── App/
    ├── config.py                     ← Settings (pydantic-settings) + get_settings()
    ├── security.py                   ← hash de contraseñas (Argon2, pwdlib) y JWT (PyJWT)
    ├── db/
    │   ├── engine.py                 ← engine + get_session()
    │   └── models/                   ← un archivo por entidad + common.py + auth.py (LoginRequest, TokenResponse)
    ├── repositories/                 ← un archivo por entidad: clase abstracta (ABC) + implementación SQL<X>Repository
    ├── service/                      ← lógica de negocio, un archivo por entidad + auth.py + errors.py
    ├── dependencies/dependencies.py  ← SessionDep, los <X>ServiceDep y CurrentUserDep
    └── routers/                      ← un router por entidad + auth.py; __init__.py decide cuáles se incluyen

Ya no quedan archivos de Mongo.
4. El patrón de cada entidad

modelos → repositorio (abstracto + SQL) → servicio → dependencia → router → probar en Scalar

Modelos (App/db/models/<entidad>.py)
Clase	Para qué
<X>Base	Campos comunes a tabla, Create y Public
<X> (table=True)	La tabla: id, claves foráneas, created_at, updated_at, índices y CHECK. No valida al construirse: nunca se usa para recibir datos de la API
<X>Create	Entrada del POST. Valida. Sin id, sin created_at, sin ids que vengan de la URL
<X>Public	Salida de la API (response_model)
<X>Update	Entrada del PATCH. Todo opcional (`| None = None`); los campos obligatorios en la tabla rechazan null explícito con reject_null

Validadores compartidos en App/db/models/common.py: utc_now, clean_name, empty_to_none, normalize_phone, validate_timezone, y constantes (NAME_MAX, EMAIL_MAX, PHONE_MAX, DESCRIPTION_MAX…).
Repositorio

    Recibe una Session. Solo habla con la base de datos; no sabe nada de HTTP.
    Métodos típicos: get (-> X | None), add, update(entity, changes), list_all / list_by_<padre> con limit, offset y order_by.
    add/update: session.add → commit (con try/except IntegrityError: rollback; raise) → refresh.

Servicio

    Recibe los repositorios que necesite (a veces varios).
    get devuelve X (sin None): convierte el None en 404.
    Comprobaciones contra lo guardado (pertenencia al padre de la URL, estado activo, reglas que combinan campos guardados + cambios) van aquí.
    Errores de unicidad: _raise_if_conflict + conflict_message(error, UNIQUE_MESSAGES) (en App/service/errors.py) → 409. UNIQUE_MESSAGES solo contiene restricciones de unicidad (nunca CHECK), con el nombre copiado exactamente del modelo o de Postgres.
    _raise_if_conflict se anota -> NoReturn.

Router

    prefix en plural o anidado (/business/{business_id}/...). El nombre de cada {parametro} del prefix debe coincidir exactamente con el parámetro de la función.
    response_model=<X>Public / list[<X>Public], status_code=201 en POST, 204 en DELETE.
    Paginación: limit: Annotated[int, Query(ge=1, le=100)] = 50, offset: Annotated[int, Query(ge=0)] = 0.

5. Estado actual
Entidad	Rutas	Estado
businesses	/business	✅
users	/users	✅
business_members	/business/{business_id}/members	✅
services	/business/{business_id}/services	✅
provider_services	/business/{business_id}/services/{service_id}/providers	✅ (clave compuesta, DELETE real)
availabilities	/business/{business_id}/members/{member_id}/availabilities	✅
customers	/business/{business_id}/customers	✅ (user_id opcional, nunca del JSON; consentimiento obligatorio)
appointments	/business/{business_id}/appointments	✅ (cita + primera fila de historial en una sola transacción, FOR UPDATE del proveedor)
appointment_status_history	/business/{business_id}/appointments/{appointment_id}/history	✅ (solo inserción; changed_by opcional)
auth	/auth/login, /auth/me	⏳ En curso (ver sección 6)

Las reglas de las citas (ends_at calculado por el servidor, zona horaria, capacidad, transiciones de estado, booking_code) están en DECISIONS.md → "Citas".
6. En curso: login y autorización

Hecho:

    Paso 1 – Contraseñas: users.password_hash con Argon2 (migración c645a529e598). POST /users recibe la contraseña; el hash nunca sale en una respuesta.
    Paso 2 – Login: POST /auth/login → access token JWT (HS256, 10 min, sub + exp). Mismo 401 para email inexistente y contraseña incorrecta; 403 si la cuenta está inactiva.
    Paso 3 – Usuario actual: get_current_user / CurrentUserDep (carga el usuario de la BD en cada petición) y GET /auth/me.

    Paso 4 (parte 1) – Columnas de roles (migración c8fa27da7e9a): users.is_platform_admin y business_members.is_owner, ambas con server_default false y fuera de los modelos Create/Update/Public. Índices únicos parciales business_members_one_owner_per_business (business_id) y business_members_one_business_per_owner (user_id), los dos WHERE is_owner, y CHECK business_members_owner_is_admin (NOT is_owner OR is_admin). El downgrade se detiene si hay dueños o administradores de la plataforma.

Siguiente:

    Paso 4 (parte 2) – Buscar miembro por (user_id, business_id) en el repositorio y dependencia require_member para las rutas /business/{business_id}/....
    Paso 5 – Proteger cada endpoint según "Permisos por endpoint" de DECISIONS.md. Hasta entonces, las rutas siguen abiertas (cualquiera puede cambiar active de usuarios, etc.).
    Pasos 6–8 – Refresh token, límite de intentos de login y auditoría.

El detalle de cada paso está en la lista personal de pendientes (docs/TODO.md, fuera de Git).
7. Pendiente para más adelante

    Endpoint de huecos libres (GET .../slots?date=...) para el frontend.
    Verificación de email, notificaciones (email primero) y creación pública de negocios.
    Tests con pytest (empezar por la lógica pura).
    Limpieza: limit por defecto de 5 en App/routers/business.py → 50, prefijo /business → /businesses (opcional).
    Restricción de solapamiento de disponibilidades a nivel de base de datos (opcional, avanzado).
    Pagos (licencia + mantenimiento): tablas futuras, no afectan al esquema actual.
    Frontend (React + TypeScript + Vite): todavía no empezado.

8. Comandos del día a día

Docker (desde la raíz del repo, con Docker Desktop abierto):

docker compose up -d
docker compose ps
docker compose logs db          # esperar "ready to accept connections"
docker compose stop
docker compose exec db psql -U app -d scheduling

Backend (desde backend/, con el venv activo):

uvicorn main:app --reload        # Scalar en http://localhost:8000/scalar
python -m scripts.print_ddl
alembic check                    # ¿modelos y BD coinciden? Ejecutar ANTES de generar migraciones
alembic revision --autogenerate -m "mensaje"   # revisar SIEMPRE el archivo generado
alembic upgrade head
pyright App
ruff check App

En psql: \dt, \d tabla, \dT, \x, \q. Las consultas SQL terminan en ;.
9. Errores que ya nos pasaron (lista de revisión)

    Mayúsculas donde no tocan: "Users", created_At, "Appointmentstatus", session.add(User) en vez de user, claves de UNIQUE_MESSAGES.
    Paginación: offset por defecto debe ser 0; no pasar offset=limit.
    Filtros: if active is not None: (no is None).
    Argumentos del mismo tipo intercambiados (dos UUID): usar argumentos por nombre. Pyright no lo detecta.
    Validadores: toda rama termina en return o raise. model_validator devuelve self. En los Update, manejar None primero.
    Tipos: repositorio get -> X | None; servicio get -> X. Un | None que no debe estar genera código muerto en otros sitios.
    No silenciar avisos (# type: ignore, # noqa) sin entender la causa. Excepciones legítimas: __tablename__ y Modelo.active == True dentro de .where(...).
    self.session.get/add dentro del repositorio, no self.get/self.add (recursión / doble commit).
    __table_args__ es una tupla (ojo con la coma); los nombres de foreign_key usan el __tablename__.
    Los límites de Pydantic (ge, gt) deben decir lo mismo que los CHECK de Postgres, en Base y en Update.
    alembic check antes de revision --autogenerate; revisar el downgrade (borrar enums con checkfirst, nombres en minúsculas).
    Si Pylance marca algo raro, contrastar con pyright en la terminal y reiniciar el language server.

