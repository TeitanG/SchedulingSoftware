Decisiones de diseño

    Registro de decisiones y su motivo. Si algo se cambia, añadir una línea nueva con la fecha en vez de borrar la anterior. Última actualización: 2026-11-20.

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
    Las migraciones se versionan en Git y nunca se editan una vez compartidas.
    (2026-11-20) Un downgrade que no se puede hacer sin perder o inventar datos no borra nada: comprueba primero y se detiene con un mensaje claro (ej. 0b9d904842cc: no vuelve changed_by a NOT NULL si hay filas con NULL).

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
    (2026-11-19) Clientes en tabla propia customers, por negocio. Sustituye a "los clientes son usuarios sin filas en business_members". Motivo (según el commit 9ae3a80): evitar problemas con la confirmación de citas. appointments.client_id apunta a customers.id.
    (2026-11-19) Un cliente puede existir sin cuenta: user_id es opcional; si lo tiene, no se repite en el mismo negocio (UNIQUE parcial business_id + user_id).
    (2026-11-19) Cliente con al menos un medio de contacto: CHECK (email IS NOT NULL OR phone_number IS NOT NULL). Email único por negocio sin distinguir mayúsculas (lower(email)) y teléfono único por negocio; ambos con índice parcial (solo cuando no son NULL).
    (2026-11-19) Consentimiento de datos personales obligatorio al crear un cliente (consent = true), guardando consent_at y consent_version. email_verified_at / phone_verified_at preparados para verificar contacto más adelante.
    (2026-11-19) customers también usa active (soft delete) y ondelete="RESTRICT": tiene citas asociadas.
    (2026-11-20) appointment_status_history.changed_by pasa a ser opcional (migración 0b9d904842cc). NULL = cambio sin usuario autenticado (reserva pública o sistema). Sustituye a "changed_by = usuario que hizo el cambio" mientras no haya login; con JWT se rellenará con el usuario del token, nunca con un id del cuerpo ni con el id de un cliente (apunta a users, no a customers).
    (2026-11-20) ends_at lo calcula el servidor: starts_at + services.duration. El cliente solo envía starts_at (resuelve la pregunta abierta de contexto.md).
    (2026-11-20) Capacidad: una cita nueva cabe si las citas pending/confirmed del mismo proveedor que se solapan son menos que services.capacity (overlapping >= capacity → 409).
    (2026-11-20) booking_code: 6 caracteres en formato XXX-XXX con alfabeto sin caracteres confusos (sin I, L, O, 0, 1), generado con secrets. Si choca con appointments_booking_code_unique se responde 409 pidiendo reintentar (31^6 ≈ 887 millones de combinaciones; reintento automático, más adelante si hace falta).
    (2026-11-20) customers.user_id nunca viene del cuerpo de la petición (no está en CustomerCreate ni en CustomerUpdate): lo asigna el servidor a partir del usuario autenticado. Motivo: si se aceptara en el JSON, cualquiera podría vincular un cliente a la cuenta de otra persona. Hasta tener login (JWT), todos los clientes se crean sin cuenta (user_id = NULL).
    (2026-11-20) consent_version lo pone el servidor (constante CONSENT_VERSION en App/service/customer.py, hoy "2026-11-19"). Cuando cambie la política de datos se actualiza la constante: los clientes nuevos guardan la versión nueva y los antiguos conservan la que aceptaron.

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
    (2026-11-20) graphify-out/ (grafo de conocimiento generado con graphify) va en .gitignore: se regenera, contiene rutas absolutas de la máquina y ensucia los diffs.
    (2026-11-20) Pendientes del proyecto en docs/TODO.md.

Negocio

    Modelo de cobro: licencia vitalicia + cuota de mantenimiento (no comisión por cita). Las tablas de pagos se diseñarán más adelante y no afectan al esquema actual.
    Un negocio con un solo profesional es un negocio con un único miembro que es admin y proveedor.
