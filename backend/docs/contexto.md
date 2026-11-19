Contexto del proyecto: SchedulingSoftware (backend)

    Documento para retomar el trabajo en una conversación nueva o para que alguien nuevo entienda el proyecto. Última actualización: 2026-11-18. Las decisiones de diseño y su motivo están en docs/DECISIONES.md.

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

El puerto es 5433 porque el 5432 daba problemas en Windows (probablemente otro Postgres local).
3. Estructura

backend/
├── main.py
├── alembic.ini / alembic/            ← migraciones (env.py usa get_settings y SQLModel.metadata)
├── scripts/print_ddl.py              ← imprime el CREATE TABLE / CREATE INDEX de todos los modelos
└── App/
    ├── config.py                     ← Settings (pydantic-settings) + get_settings()
    ├── db/
    │   ├── engine.py                 ← engine + get_session()
    │   └── models/                   ← un archivo por entidad + common.py
    ├── repositories/
    │   ├── repositories.py           ← clases abstractas (contratos)
    │   └── sql_repositories.py       ← implementaciones con SQLModel
    ├── service/                      ← lógica de negocio, un archivo por entidad + errors.py
    ├── dependencies/dependencies.py  ← SessionDep y los <X>ServiceDep
    └── routers/                      ← un router por entidad; __init__.py decide cuáles se incluyen

Archivos antiguos de Mongo (schemas/, *_service.py, fastapidependencies.py, core/…) se van borrando a medida que se migra cada entidad. Si un archivo sigue con nombre *_service.py, todavía no está migrado.
4. El patrón de cada entidad

modelos → repositorio (abstracto + SQL) → servicio → dependencia → router → probar en Scalar

Modelos (App/db/models/<entidad>.py)
Clase	Para qué
<X>Base	Campos comunes a tabla, Create y Public
<X> (table=True)	La tabla: id, claves foráneas, created_at, updated_at, índices y CHECK. No valida al construirse: nunca se usa para recibir datos de la API
<X>Create	Entrada del POST. Valida. Sin id, sin created_at, sin ids que vengan de la URL
<X>Public	Salida de la API (response_model)
<X>Update	Entrada del PATCH. Todo `

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
availabilities	/business/{business_id}/members/{member_id}/availabilities	✅ (revisar que el prefix use {member_id})
appointments + appointment_status_history	—	⏳ Siguiente
6. Siguiente: citas (appointments)

Las tablas ya existen (migración inicial). Falta todo lo demás. Puntos a resolver:

    Transacciones: crear una cita guarda la cita y su primera fila de historial; deben guardarse las dos o ninguna. El repositorio actual hace commit en cada add, así que hay que cambiar el enfoque para este caso.
    Zonas horarias: la cita es un instante (TIMESTAMPTZ, UTC). La disponibilidad es hora local del negocio (businesses.timezone). Para validar: convertir starts_at a la zona del negocio → sacar día de la semana y hora local → comparar con availabilities. Nunca usar .replace(tzinfo=None).
    Cabe en algún bloque: la cita debe caber en alguno de los bloques activos del proveedor ese día (any()), no solo en el primero.
    Capacidad: contar citas pending/confirmed del mismo proveedor que se solapan y comparar con services.capacity (consulta SQL; índice appointments_provider_starts ya existe).
    El proveedor ofrece ese servicio (provider_services), y proveedor/servicio activos y del mismo negocio.
    Transiciones de estado: pending → confirmed | canceled, confirmed → completed | canceled. Cada cambio escribe una fila en el historial.
    booking_code legible (tipo K7M-29Q), único.

Pregunta abierta antes de los modelos: ¿quién calcula ends_at? (Recomendación: el servidor, a partir de services.duration.)
7. Pendiente para más adelante

    Endpoint de huecos libres (GET .../slots?date=...) para el frontend.
    Login y permisos (JWT). El actor nunca debe venir del cuerpo de la petición. Hoy cualquiera puede cambiar active de usuarios, etc. changed_by del historial necesita el usuario autenticado.
    Tests con pytest (empezar por la lógica pura).
    Limpieza: borrar archivos antiguos de Mongo, rehacer requirements.txt (separar requirements-dev.txt), subir los limit por defecto que quedaron en 5, prefijo /business → /businesses (opcional).
    Restricción de solapamiento de disponibilidades a nivel de base de datos (opcional, avanzado).
    Pagos (licencia + mantenimiento): tablas futuras, no afectan al esquema actual.

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

