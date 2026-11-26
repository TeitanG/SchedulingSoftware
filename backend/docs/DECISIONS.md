Decisiones de diseño

    Decisiones vigentes del proyecto y su motivo. Cuando una decisión cambia, se reescribe en su forma actual y se borra lo que deja de aplicar; el historial de cambios queda en Git. Última actualización: 2026-11-26.

Base de datos

    PostgreSQL en lugar de MongoDB. El dominio es relacional (usuarios, negocios, servicios, horarios, citas). Postgres impone claves foráneas, tipos, UNIQUE y CHECK; muchos bugs del backend de Mongo eran fallos silenciosos que Postgres convierte en errores visibles.
    SQLModel + Alembic. Modelos tipo Pydantic (familiares con FastAPI) y migraciones versionadas en Git desde el primer día.
    IDs UUIDv4 (uuid.uuid4). No se pueden adivinar ni revelan volumen. Se descartaron IDs secuenciales/legibles como clave primaria. Se puede pasar a UUIDv7 más adelante sin migrar (la columna sigue siendo UUID).
    Códigos legibles aparte: las citas tienen booking_code (tipo K7M-29Q) solo para mostrar; el id interno sigue siendo UUID.
    Nombres: tablas en plural y minúsculas (business_members); clases en singular y PascalCase; columnas y restricciones en snake_case minúsculas, con el nombre de la tabla como prefijo (services_price_positive).
    Las reglas viven en dos sitios: en Postgres (CHECK, UNIQUE, NOT NULL) como red de seguridad, y en Pydantic para responder 422 con mensaje claro. Deben decir lo mismo.
    Unicidad sin distinguir mayúsculas con índices sobre lower(...): email de negocio, email de usuario, nombre de servicio por negocio (business_id + lower(name)).
    El nombre del negocio no es único (pendiente: migración que quita businesses_name_unique). Motivo: con la creación pública de negocios, el primero que registra un nombre se lo quedaría y un impostor podría bloquear al negocio real; además hay negocios legítimos con el mismo nombre (independientes sin registro mercantil, otras ciudades u otros países). Lo que identifica a un negocio es su link, no su nombre.
    Enums de Postgres con nombre = valor, en minúsculas (Postgres guarda el nombre del miembro del enum). Añadir valores requiere migración.
    active en lugar de borrar (soft delete) para usuarios, negocios, miembros, servicios, horarios y clientes: tienen historia (citas) que no se puede perder. ondelete="RESTRICT" en esas claves foráneas.
    Borrado real en provider_services: la fila solo representa la relación y nada apunta a ella; las citas referencian al miembro y al servicio directamente.
    created_at / updated_at con TIMESTAMPTZ y utc_now(); updated_at con onupdate de SQLAlchemy (no cubre cambios hechos con SQL a mano).
    Índices pensados para consultas frecuentes: appointments(provider_id, starts_at) y appointment_status_history(appointment_id, changed_at). Postgres no indexa claves foráneas automáticamente.
    Bloqueo FOR UPDATE del proveedor al crear citas para evitar overbooking.
    Las migraciones se versionan en Git y nunca se editan una vez compartidas.
    El autogenerado de Alembic no detecta cambios dentro de un CHECK: esas migraciones se escriben a mano (ej. 8353b73d7dd1, precio > 0).
    Añadir una columna obligatoria a una tabla con datos se hace en tres pasos dentro de la migración: columna opcional, rellenar las filas existentes, columna obligatoria (ej. c645a529e598, password_hash).
    Un downgrade que no se puede hacer sin perder o inventar datos no borra nada: comprueba primero y se detiene con un mensaje claro (ej. 0b9d904842cc, 188a2956d872, c645a529e598).

Modelo de dominio

    users = la persona; business_members = su papel en un negocio (is_owner, is_admin, is_provider). Una persona puede estar en varios negocios con roles distintos.
    Un miembro debe tener al menos un rol (CHECK (is_admin OR is_provider)) y no puede repetirse en el mismo negocio (UNIQUE (user_id, business_id)).
    Un servicio lo pueden ofrecer varios proveedores → tabla provider_services con clave primaria compuesta (member_id, service_id).
    Capacidad en el servicio, no en el horario.
    Moneda en el negocio (COP / USD), no en el servicio: un negocio cobra en una sola moneda. No se puede cambiar con PATCH (cambiaría el significado de todos los precios).
    Precio en INTEGER en la unidad mínima de la moneda (nunca float). No hay servicios gratuitos: price_amount > 0 en Pydantic (gt=0) y en Postgres (CHECK services_price_positive).
    Zona horaria por negocio (nombre IANA, por defecto America/Bogota), lista para negocios en EE. UU. (varias zonas y horario de verano). Con las locaciones pasará a la sede.
    Disponibilidad = hora de reloj local (TIME, una fila por bloque y día). Cita = instante (TIMESTAMPTZ, UTC). Para validar, convertir la cita a la zona del negocio.
    Duración del servicio en minutos (duration).
    Teléfonos en formato internacional E.164 (+573001234567); se exige el prefijo de país, sin columna de región.
    Dirección / descripción vacías se guardan como NULL (empty_to_none); los nombres se limpian con strip() (clean_name).
    Las citas y los bloques no pueden cruzar la medianoche. Si un cliente necesita turnos nocturnos, ver la opción de bloques con end_time < start_time.

    Clientes
        Tabla propia customers, por negocio. appointments.client_id apunta a customers.id.
        Un cliente puede existir sin cuenta: user_id es opcional; si lo tiene, no se repite en el mismo negocio (UNIQUE parcial business_id + user_id).
        customers.user_id nunca viene del cuerpo de la petición (no está en CustomerCreate ni en CustomerUpdate): lo asigna el servidor a partir del usuario autenticado. Motivo: si se aceptara en el JSON, cualquiera podría vincular un cliente a la cuenta de otra persona.
        Al menos un medio de contacto: CHECK (email IS NOT NULL OR phone_number IS NOT NULL). Email único por negocio sin distinguir mayúsculas (lower(email)) y teléfono único por negocio; ambos con índice parcial (solo cuando no son NULL).
        Consentimiento de datos personales obligatorio al crear un cliente (consent = true), guardando consent_at y consent_version. consent_version lo pone el servidor (constante CONSENT_VERSION en App/service/customer.py): los clientes nuevos guardan la versión vigente y los antiguos conservan la que aceptaron.
        email_verified_at / phone_verified_at preparados para verificar el contacto más adelante.

    Citas
        ends_at lo calcula el servidor: starts_at + services.duration. El cliente solo envía starts_at.
        Capacidad: una cita nueva cabe si las citas pending/confirmed del mismo proveedor que se solapan son menos que services.capacity (overlapping >= capacity → 409).
        booking_code: 6 caracteres en formato XXX-XXX con alfabeto sin caracteres confusos (sin I, L, O, 0, 1), generado con secrets. Si choca con appointments_booking_code_unique se responde 409 pidiendo reintentar (31^6 ≈ 887 millones de combinaciones).
        Historial de estados en tabla aparte (appointment_status_history), solo de inserción (sin updated_at). changed_by es opcional: NULL = cambio sin usuario autenticado (reserva pública o sistema). Con usuario, sale siempre del token, nunca de un id del cuerpo ni del id de un cliente (apunta a users, no a customers).

Negocios

    Creación pública: cualquier usuario con el email verificado puede crear un negocio y queda como su propietario. Motivo: que el negocio empiece a usar el software sin reuniones ni chats; cada paso manual antes de empezar es un cliente que se pierde. Hasta que exista la verificación de email, solo la plataforma crea negocios.
    Un usuario puede ser propietario de un solo negocio, pero puede ser miembro (por ejemplo, proveedor) de otros: un estilista puede trabajar en dos peluquerías con la misma cuenta.
    Propietario: business_members.is_owner. Reglas en Postgres, no solo en el código:
        Un solo propietario por negocio: índice único parcial UNIQUE (business_id) WHERE is_owner.
        Un usuario es propietario de un solo negocio: índice único parcial UNIQUE (user_id) WHERE is_owner.
        El propietario siempre es admin: CHECK (NOT is_owner OR is_admin).
    Un negocio con un solo profesional es un negocio con un único miembro que es propietario, admin y proveedor.
    Locaciones: un negocio puede tener muchas sedes (ejemplo: Crepes & Waffles, un solo negocio con muchas locaciones). Pendiente de diseñar.
    Prueba gratuita de 15 días para cada negocio nuevo, con recordatorios durante los últimos 5 días. Si no paga al terminar la prueba, el negocio pasa a active = false.
    Pagos: fuera de alcance por ahora; el modelo de cobro se diseñará aparte.
    Suplantación: no se verifica a cada negocio (es imposible). Se reduce el daño con términos de uso que la prohíben, un proceso de denuncia (la plataforma desactiva o renombra el negocio falso) y la verificación para aparecer en la página pública (V2).
    Reservas (V1): un cliente llega a reservar mediante el link que cada negocio comparte. No hay listado de negocios.
    Página pública (V2): un negocio puede aparecer como público para cualquier usuario registrado, que puede reservar con él (se crea su Customer con user_id del token). Da visibilidad a los negocios dentro de la plataforma; posible función de pago adicional. Solo pueden ser públicos los negocios verificados con documentos (certificado de existencia y representación legal de la Cámara de Comercio o RUT); en una disputa por un nombre tiene prioridad el verificado. Motivo: en la V1 el riesgo de suplantación es bajo porque los clientes llegan por el link que publica el propio negocio; en la página pública los clientes buscan, y ahí un impostor sí haría daño.

Autenticación y autorización

    Prioridad: seguridad. Ante la duda, la opción que revela menos información y concede menos permisos.

    Contraseñas
        Se guarda solo el hash (Argon2, pwdlib), en users.password_hash. Nunca la contraseña, nunca en texto plano. password_hash no aparece en ningún modelo Public ni en ninguna respuesta.
        Hash lento a propósito (Argon2/bcrypt, no SHA-256): hace inviable probar contraseñas en masa si se roba la base de datos.
        Contraseña de 8 a 128 caracteres. Cambiar la contraseña será un endpoint aparte que pida la actual (no va en UserUpdate).
        Los usuarios creados antes de las contraseñas tienen password_hash = '!', que nunca coincide: deben restablecer su contraseña.

    Tokens y sesión
        Access token: JWT firmado con SECRET_KEY (en .env, nunca en el código ni en Git), algoritmo HS256. Dura 10 minutos. Contenido mínimo: sub = user_id y exp. El contenido de un JWT se puede leer (no está cifrado): nunca se mete nada sensible.
        Al leer un token se exigen la firma, exp y sub, y solo se acepta HS256 (protege contra tokens con alg: none).
        En cada petición se carga el usuario de la base de datos: desactivar una cuenta tiene efecto inmediato aunque su token siga vigente.
        Refresh token: sirve solo para pedir un access token nuevo sin volver a escribir la contraseña. Dura 10 minutos y cada uso entrega uno nuevo de otros 10 (sesión deslizante): la sesión sigue viva mientras el usuario esté activo y termina tras unos 10–20 minutos de inactividad, al cerrar sesión o a las 8 horas como máximo absoluto. Se guarda en la base de datos solo como hash, es de un solo uso y se puede revocar (cerrar sesión, desactivar cuenta).
        Almacenamiento en el frontend: refresh token en una cookie httpOnly (con Secure y SameSite), que el JavaScript de la página no puede leer; access token solo en memoria. Nunca en localStorage ni en caché: cualquier script inyectado (XSS) podría robarlos.

    Login
        Email inexistente y contraseña incorrecta devuelven el mismo 401 con el mismo mensaje ("Incorrect email or password"): no se revela quién tiene cuenta. Excepción consciente a la regla 404 de la API.
        El email se busca sin distinguir mayúsculas (lower(email)).
        Credenciales correctas pero usuario inactivo: 403 "Account is inactive" (ya demostró ser el dueño) y se le indica el proceso de reactivación.
        Límite de intentos: a partir de 4 fallos, bloqueo temporal y creciente (no cambio de contraseña obligatorio), contando por IP. Motivo: forzar un cambio de contraseña permitiría a cualquiera bloquear a otra persona solo con conocer su email. Pendiente de confirmar: contar por la pareja IP + cuenta, para que un atacante no pueda bloquear al usuario real, que entra desde otra IP.

    Registro y prevención de spam
        Registro libre: cualquiera puede crear una cuenta (POST /users público). Una cuenta nueva no tiene ningún permiso sobre ningún negocio.
        Contra las cuentas falsas y el spam: para crear un negocio hace falta el email verificado, y cada usuario puede ser propietario de un solo negocio. Los negocios que no pagan tras la prueba quedan inactivos.
        Medidas adicionales propuestas (pendientes de decidir el detalle): límite de registros y de creación de negocios por IP; CAPTCHA invisible en el registro y en la creación de negocios; rechazo de emails desechables; limpieza de cuentas que nunca verifican su email; proceso de denuncia de negocios falsos.

    Roles
        Propietario: quien crea el negocio. Todo lo del admin, más crear, ascender (is_admin) y desactivar admins. Siempre es admin.
        Admin: gestiona el negocio (proveedores, servicios, clientes, citas). No puede tocar a otros admins ni al propietario.
        Proveedor: su propia disponibilidad y sus propias citas.
        Administrador de la plataforma (users.is_platform_admin): desactivar y reactivar negocios, cambiar el propietario de un negocio y dar soporte con autorización del cliente.
        Cambiar el propietario es solo del administrador de la plataforma, siguiendo un SOP pendiente de escribir. Motivo: el propietario es la llave del negocio; si le roban la cuenta, el ladrón no puede quedarse el negocio transfiriéndolo a otra cuenta, y si el dueño real pierde el acceso, la plataforma lo recupera verificando su identidad fuera del sistema.
        Acceso de soporte: el administrador de la plataforma no entra a los datos de un negocio por defecto. Solo con un código único que genera el propio cliente; el acceso caduca, se puede revocar y queda en la auditoría. Motivo: privacidad de los clientes y que la cuenta de la plataforma no sea una llave a todos los datos.
        is_platform_admin no está en UserCreate, UserUpdate ni UserPublic: ningún endpoint lo puede conceder. Para concederlo se usará un código generado en el servidor, de un solo uso y con caducidad corta, guardado solo como hash e invalidado al usarse. Nunca un secreto fijo en el código, en un script del repositorio ni en el .env: si se filtrara, cualquiera podría hacerse administrador de toda la plataforma. Diseño exacto pendiente: quién genera el código y cómo llega a quien lo usa.

    Permisos por endpoint
        Usuarios: registrarse → público. Listar todos → plataforma. Ver uno → el propio usuario o la plataforma. Editar nombre y email → solo el propio usuario. Cambiar active → plataforma.
        Negocios: crear → usuario con email verificado que no sea ya propietario de otro (provisionalmente, solo la plataforma). Listar todos → plataforma. Ver uno → miembros. Editar datos → propietario y admins. Cambiar active → plataforma.
        Miembros: añadir, activar o desactivar proveedores → propietario y admins. Añadir, ascender (is_admin) o desactivar admins → propietario. Cambiar el propietario → plataforma. Listar y ver → propietario y admins.
        Servicios y proveedores de un servicio: crear, editar y asignar → propietario y admins. Ver → miembros.
        Disponibilidad: propietario y admins gestionan la de cualquier proveedor; un proveedor gestiona solo la suya. Ver → miembros.
        Clientes: crear, ver y editar → miembros.
        Citas: crear → propietario y admins para cualquier proveedor; un proveedor solo para sí mismo (otro provider_id → 403). Listar → propietario y admins todas; un proveedor solo las suyas. Estado, notas e historial → propietario y admins; un proveedor solo los de sus citas.

    Códigos de error
        401: sin token, token inválido o caducado, o el usuario del token no existe o está inactivo. Mismo mensaje en todos los casos ("Could not validate credentials") y cabecera WWW-Authenticate: Bearer.
        404: el usuario no es miembro del negocio de la URL, el miembro está desactivado o el negocio no existe. Mismo código en todos los casos para no revelar qué negocios existen.
        403: es miembro del negocio, pero su rol no le permite la acción (ya sabe que el negocio existe, no se revela nada).
        Negocio desactivado: nadie trabaja en él. Quien no es miembro recibe 404 (como siempre); un miembro recibe 403 "Business is inactive".

    Actor
        El usuario que hace la acción sale siempre del token, nunca del cuerpo de la petición (changed_by del historial, customers.user_id).

    Reactivación
        Usuarios y clientes: solo mediante verificación por correo electrónico (enlace o código de un solo uso y con caducidad).
        Negocios: solo el administrador de la plataforma.

    Auditoría
        Obligatoria: se registran los intentos de login (fallidos y correctos), los bloqueos, los accesos de soporte y las acciones del administrador de la plataforma (quién, qué, cuándo y desde qué IP).

    Notificaciones
        Se empieza solo con email. Se diseña para crecer: los servicios envían a través de una interfaz abstracta (como los repositorios, con ABC) y el email es la primera implementación; SMS y WhatsApp se añaden después como implementaciones nuevas sin tocar la lógica que las usa.

API

    Capas: router (HTTP) → servicio (reglas de negocio, decide códigos HTTP) → repositorio (solo base de datos).
    Rutas anidadas para recursos que pertenecen a otro (/business/{business_id}/members/...). El servicio siempre comprueba que el recurso pertenece al padre de la URL (404 si no).
    Solo PATCH para actualizar (sin PUT). model_dump(exclude_unset=True): solo se cambian los campos enviados; null explícito solo en campos opcionales (los obligatorios lo rechazan con reject_null).
    Códigos de error (además de los de autenticación):
        404: el recurso (o un id referenciado, como user_id) no existe o no pertenece al padre.
        409: conflicto con el estado actual (duplicado, recurso inactivo, solapamiento, transición de estado no permitida).
        422: dato inválido (validaciones de Pydantic y reglas que combinan campos, como roles o start_time < end_time).
        Listas vacías → 200 con [], nunca 404.
    Formato de error: detail={"Error": "mensaje"} en todos los HTTPException. Mensajes en inglés.
    Paginación en todos los listados (limit 1–100, offset ≥ 0) y siempre con order_by estable (id como último criterio).
    Errores de unicidad se traducen a 409 por el nombre de la restricción (UNIQUE_MESSAGES); cualquier otra violación de integridad se deja pasar (500) para detectar validaciones que faltan.
    Endpoints síncronos (def) porque la sesión de base de datos es síncrona.
    Comprobaciones previas en el servicio (existencia y active de usuario/negocio/miembro) además de las claves foráneas, porque la base de datos no puede comprobar el estado active.
    Repositorios escritos a mano (sin clase base genérica) por legibilidad; revisar con la "regla de tres" si la repetición molesta.

Herramientas y entorno

    PostgreSQL 17 en Docker, puerto local 5433.
    Configuración con pydantic-settings: la app no arranca si faltan DATABASE_URL o SECRET_KEY.
    ESLint (no Oxlint, por ahora) y Prettier para el frontend; Ruff y Pyright para el backend.
    Frontend: React + TypeScript + Vite, con datos falsos primero y una capa api/ aislada.
    graphify-out/ (grafo de conocimiento generado con graphify) va en .gitignore: se regenera, contiene rutas absolutas de la máquina y ensucia los diffs.
    La lista de pendientes es personal y no forma parte del repositorio.
