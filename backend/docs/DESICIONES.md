Decisiones de diseño

    Registro de decisiones y su motivo. Si algo se cambia, añadir una línea nueva con la fecha en vez de borrar la anterior. Última actualización: 2026-11-18.

Base de datos

    PostgreSQL en lugar de MongoDB. El dominio es relacional (usuarios, negocios, servicios, horarios, citas). Postgres impone claves foráneas, tipos, UNIQUE y CHECK; muchos bugs del backend de Mongo eran fallos silenciosos que Postgres convierte en errores visibles.
    SQLModel + Alembic. Modelos tipo Pydantic (familiares con FastAPI) y migraciones versionadas en Git desde el primer día.
    IDs UUIDv4 (uuid.uuid4). No se pueden adivinar ni revelan volumen. Se descartaron IDs secuenciales/legibles como clave primaria. Se puede pasar a UUIDv7 más adelante sin migrar (la columna sigue siendo UUID).
    Códigos legibles aparte: las citas tendrán booking_code (tipo K7M-29Q) solo para mostrar; el id interno sigue siendo UUID.
    Nombres: tablas en plural y minúsculas (business_members); clases en singular y PascalCase; columnas y restricciones en snake_case minúsculas, con el nombre de la tabla como prefijo (services_price_non_negative).
    Las reglas viven en dos sitios: en Postgres (CHECK, UNIQUE, NOT NULL) como red de seguridad, y en Pydantic para responder 422 con mensaje claro. Deben decir lo mismo.
    Unicidad sin distinguir mayúsculas con índices sobre lower(...): nombre y email de negocio, email de usuario, nombre de servicio por negocio (business_id + lower(name)).
    Enums de Postgres con nombre = valor, en minúsculas (Postgres guarda el nombre del miembro del enum). Añadir valores requiere migración.
    active en lugar de borrar (soft delete) para usuarios, negocios, miembros, servicios y horarios: tienen historia (citas) que no se puede perder. ondelete="RESTRICT" en esas claves foráneas.
    Borrado real en provider_services: la fila solo representa la relación y nada apunta a ella; las citas referencian al miembro y al servicio directamente.
    created_at / updated_at con TIMESTAMPTZ y utc_now(); updated_at con onupdate de SQLAlchemy (no cubre cambios hechos con SQL a mano).
    Índices pensados para consultas frecuentes: appointments(provider_id, starts_at) y appointment_status_history(appointment_id, changed_at). Postgres no indexa claves foráneas automáticamente.
    Bloqueo FOR UPDATE del proveedor al crear citas para evitar overbooking

Modelo de dominio

    users = la persona; business_members = su papel en un negocio (is_admin, is_provider). Una persona puede estar en varios negocios con roles distintos. Los clientes son usuarios sin filas en business_members.
    Un miembro debe tener al menos un rol (CHECK (is_admin OR is_provider)) y no puede repetirse en el mismo negocio (UNIQUE (user_id, business_id)).
    Un servicio lo pueden ofrecer varios proveedores → tabla provider_services con clave primaria compuesta (member_id, service_id).
    Capacidad en el servicio, no en el horario.
    Moneda en el negocio (COP / USD), no en el servicio: un negocio cobra en una sola moneda. No se puede cambiar con PATCH (cambiaría el significado de todos los precios).
    Precio en INTEGER en la unidad mínima de la moneda (nunca float).
    Zona horaria por negocio (nombre IANA, por defecto America/Bogota), lista para negocios en EE. UU. (varias zonas y horario de verano).
    Disponibilidad = hora de reloj local (TIME, una fila por bloque y día). Cita = instante (TIMESTAMPTZ, UTC). Para validar, convertir la cita a la zona del negocio.
    Duración del servicio en minutos (duration).
    Teléfonos en formato internacional E.164 (+573001234567); se exige el prefijo de país, sin columna de región.
    Dirección / descripción vacías se guardan como NULL (empty_to_none); los nombres se limpian con strip() (clean_name).
    Historial de estados de citas en tabla aparte (appointment_status_history), solo de inserción (sin updated_at), con changed_by = usuario que hizo el cambio.
    Las citas y los bloques no pueden cruzar la medianoche. Si un cliente necesita turnos nocturnos, ver la opción de bloques con end_time < start_time

API

    Capas: router (HTTP) → servicio (reglas de negocio, decide códigos HTTP) → repositorio (solo base de datos).
    Rutas anidadas para recursos que pertenecen a otro (/business/{business_id}/members/...). El servicio siempre comprueba que el recurso pertenece al padre de la URL (404 si no).
    Solo PATCH para actualizar (sin PUT). model_dump(exclude_unset=True): solo se cambian los campos enviados; null explícito solo en campos opcionales (los obligatorios lo rechazan con reject_null).
    Códigos de error:
        404: el recurso (o un id referenciado, como user_id) no existe o no pertenece al padre.
        409: conflicto con el estado actual (duplicado, recurso inactivo, solapamiento).
        422: dato inválido (validaciones de Pydantic y reglas que combinan campos, como roles o start_time < end_time).
        Listas vacías → 200 con [], nunca 404.
    Formato de error: detail={"Error": "mensaje"} en todos los HTTPException. Mensajes en inglés.
    Paginación en todos los listados (limit 1–100, offset ≥ 0) y siempre con order_by estable.
    Errores de unicidad se traducen a 409 por el nombre de la restricción (UNIQUE_MESSAGES); cualquier otra violación de integridad se deja pasar (500) para detectar validaciones que faltan.
    Endpoints síncronos (def) porque la sesión de base de datos es síncrona.
    Comprobaciones previas en el servicio (existencia y active de usuario/negocio/miembro) además de las claves foráneas, porque la base de datos no puede comprobar el estado active.
    Repositorios escritos a mano (sin clase base genérica) por legibilidad; revisar con la "regla de tres" si la repetición molesta.

Herramientas y entorno

    PostgreSQL 17 en Docker, puerto local 5433.
    Configuración con pydantic-settings: la app no arranca si falta DATABASE_URL.
    ESLint (no Oxlint, por ahora) y Prettier para el frontend; Ruff y Pyright para el backend.
    Frontend: React + TypeScript + Vite, con datos falsos primero y una capa api/ aislada.

Negocio

    Modelo de cobro: licencia vitalicia + cuota de mantenimiento (no comisión por cita). Las tablas de pagos se diseñarán más adelante y no afectan al esquema actual.
    Un negocio con un solo profesional es un negocio con un único miembro que es admin y proveedor.
