# SchedulingSoftware

Software de agendamiento de citas para negocios: proveedores, servicios, horarios, clientes y citas con historial de estados.

> 🚧 **Proyecto en desarrollo.** El backend (API REST) está en construcción; el frontend todavía no se ha empezado.

---

## Características

- **Negocios** con su propia zona horaria (IANA) y moneda (COP / USD).
- **Usuarios y miembros:** una persona puede pertenecer a varios negocios con roles distintos (administrador, proveedor o ambos).
- **Servicios** con duración, precio y capacidad (citas simultáneas permitidas).
- **Proveedores por servicio:** cada servicio lo pueden ofrecer varios proveedores.
- **Disponibilidad** semanal por proveedor, en hora local del negocio, con detección de solapamientos.
- **Clientes por negocio**, con o sin cuenta de usuario, y consentimiento de datos personales.
- **Citas** con validación completa al reservar:
  - el proveedor ofrece el servicio y está activo,
  - la cita cabe en un bloque de disponibilidad (convirtiendo a la zona horaria del negocio),
  - no se supera la capacidad del servicio,
  - no se reserva en el pasado ni cruzando la medianoche,
  - bloqueo `FOR UPDATE` del proveedor para evitar *overbooking* con reservas simultáneas.
- **Estados de cita** con transiciones controladas (`pending → confirmed | canceled`, `confirmed → completed | canceled`) e **historial** de cada cambio.
- **Código de reserva** legible (`K7M-29Q`), independiente del identificador interno (UUID).

## Stack

| Pieza | Tecnología |
|---|---|
| Lenguaje | Python 3.13 |
| API | FastAPI |
| ORM / modelos | SQLModel + SQLAlchemy 2 |
| Base de datos | PostgreSQL 17 (Docker) |
| Driver | psycopg 3 |
| Migraciones | Alembic |
| Configuración | pydantic-settings |
| Documentación de la API | Scalar (`/scalar`) |
| Calidad | Ruff (lint y formato) y Pyright (tipos) |
| Frontend (previsto) | React + TypeScript + Vite |

## Arquitectura

Cada entidad sigue el mismo patrón en capas:

```
router (HTTP)  →  servicio (reglas de negocio)  →  repositorio (base de datos)
```

- **Router:** define las rutas, valida la entrada con los modelos `Create` / `Update` y la salida con `Public`.
- **Servicio:** aplica las reglas (pertenencia al negocio, estado activo, transiciones…) y decide los códigos HTTP.
- **Repositorio:** solo habla con la base de datos; no sabe nada de HTTP.

Las reglas de datos viven en dos sitios que dicen lo mismo: en **PostgreSQL** (`CHECK`, `UNIQUE`, `NOT NULL`) como red de seguridad y en **Pydantic** para responder `422` con un mensaje claro.

Las decisiones de diseño y su motivo están documentadas en [`backend/docs/DESICIONES.md`](backend/docs/DESICIONES.md).

## Estructura del proyecto

```
SchedulingSoftware/
├── docker-compose.yml          # PostgreSQL 17
├── backend/
│   ├── main.py                 # punto de entrada de FastAPI
│   ├── alembic/                # migraciones
│   ├── scripts/print_ddl.py    # imprime el DDL de todos los modelos
│   ├── docs/                   # contexto, decisiones y pendientes
│   └── App/
│       ├── config.py           # configuración (lee .env)
│       ├── db/
│       │   ├── engine.py       # engine + sesión
│       │   └── models/         # un archivo por entidad
│       ├── repositories/       # acceso a datos (abstracto + SQL)
│       ├── service/            # lógica de negocio
│       ├── dependencies/       # inyección de dependencias
│       └── routers/            # un router por entidad
└── frontend/                   # (por empezar)
```

## Puesta en marcha

### Requisitos

- [Python 3.13](https://www.python.org/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### 1. Clonar el repositorio

```bash
git clone https://github.com/TeitanG/SchedulingSoftware.git
cd SchedulingSoftware
```

### 2. Levantar la base de datos

Desde la raíz del repositorio, con Docker Desktop abierto:

```bash
docker compose up -d
docker compose logs db      # esperar a "ready to accept connections"
```

PostgreSQL queda expuesto en el puerto local **5433**.

### 3. Crear el entorno virtual e instalar dependencias

```bash
cd backend
python -m venv venv

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Configurar las variables de entorno

Crea un archivo `backend/.env` (no se sube a Git):

```env
DATABASE_URL=postgresql+psycopg://app:app@localhost:5433/scheduling
SQL_ECHO=false
```

Los valores coinciden con los de `docker-compose.yml`, pensados **solo para desarrollo local**. La aplicación no arranca si falta `DATABASE_URL`.

### 5. Aplicar las migraciones

```bash
alembic upgrade head
```

### 6. Arrancar la API

```bash
uvicorn main:app --reload
```

La documentación interactiva queda en **http://localhost:8000/scalar**.

## API

Todos los recursos que pertenecen a un negocio usan rutas anidadas. El servicio comprueba siempre que el recurso pertenece al negocio de la URL (`404` si no).

| Recurso | Ruta base | Operaciones |
|---|---|---|
| Negocios | `/business` | crear, listar, obtener, actualizar |
| Usuarios | `/users` | crear, listar, obtener, actualizar |
| Miembros | `/business/{business_id}/members` | crear, listar, obtener, actualizar |
| Servicios | `/business/{business_id}/services` | crear, listar, obtener, actualizar |
| Proveedores de un servicio | `/business/{business_id}/services/{service_id}/providers` | añadir, listar, quitar |
| Disponibilidad | `/business/{business_id}/members/{member_id}/availabilities` | crear, listar, obtener, actualizar |
| Clientes | `/business/{business_id}/customer` | crear, listar, obtener, actualizar |
| Citas | `/business/{business_id}/appointments` | crear, listar (filtro por estado), obtener, cambiar estado, editar notas |
| Historial de una cita | `/business/{business_id}/appointments/{appointment_id}` | listar |

### Convenciones

- **Actualizaciones solo con `PATCH`**: únicamente se cambian los campos enviados.
- **Borrado lógico** (`active = false`) para entidades con historia; borrado real solo en la relación proveedor–servicio.
- **Paginación** en todos los listados: `limit` (1–100, por defecto 50) y `offset` (≥ 0).
- **Errores** con el formato `{"detail": {"Error": "mensaje"}}`:

| Código | Significado |
|---|---|
| `404` | El recurso no existe o no pertenece al negocio de la URL |
| `409` | Conflicto con el estado actual (duplicado, inactivo, sin capacidad, transición no permitida) |
| `422` | Dato inválido |

## Desarrollo

Desde `backend/`, con el entorno virtual activo:

```bash
ruff check App              # lint
ruff format App             # formato
pyright App                 # tipos

alembic check               # ¿coinciden modelos y base de datos?
alembic revision --autogenerate -m "mensaje"   # revisar SIEMPRE el archivo generado
alembic upgrade head

python -m scripts.print_ddl # ver el SQL de todas las tablas
```

## Hoja de ruta

- [ ] Login y permisos con JWT
- [ ] Endpoint de huecos libres para reservar (`/slots`)
- [ ] Tests con pytest
- [ ] Frontend con React + TypeScript + Vite
- [ ] Pagos (licencia + mantenimiento)

La lista detallada de pendientes está en [`backend/docs/TODO.md`](backend/docs/TODO.md).
