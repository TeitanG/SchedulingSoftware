# TODO — SchedulingSoftware (backend)

Lista de lo que falta por hacer. Última revisión: 2026-11-23.
Marca con `[x]` lo que vayas terminando. Las decisiones y su motivo van en `DECISIONES.md`; el contexto general, en `contexto.md`.

Al terminar cada bloque: `pyright --pythonpath .\venv\Scripts\python.exe App`, `ruff check App`, `ruff format App` y probar en `/scalar` que **todas** las rutas aparecen con los parámetros correctos (path, no query).

---

## 🔐 0. Login y autorización (en curso)

Decisiones tomadas: ver "Autenticación y autorización" en `DECISIONES.md`. Cada paso se prueba en Scalar antes de pasar al siguiente.

- [ ] **Paso 1 – Contraseñas.** Migración: `users.password_hash`. `POST /users` (registro libre) recibe la contraseña y guarda el hash con Argon2 (`pwdlib[argon2]`). Comprobar que `password_hash` no sale en ninguna respuesta.
- [ ] **Paso 2 – Login.** `POST /auth/login` → access token JWT (`PyJWT`) de 10 min con `sub` y `exp`. `SECRET_KEY` y duración en `config.py` / `.env` (y en `.env.example` con un valor de ejemplo, nunca el real). Mismo 401 para email inexistente y contraseña incorrecta.
- [ ] **Paso 3 – Usuario actual.** Dependencia `get_current_user` (`CurrentUserDep`) y `GET /auth/me` para probar el token.
- [ ] **Paso 4 – Roles.** `users.is_platform_admin` (migración; fuera de `UserCreate` / `UserUpdate`). Dependencia tipo `require_member(business_id, admin=...)`: no miembro → 404, miembro sin permiso → 403.
- [ ] **Paso 5 – Proteger endpoints**, uno a uno:
  - `POST /business` y reactivar negocios → solo administrador de la plataforma.
  - Miembros: el admin del negocio crea y desactiva **proveedores**; crear, ascender (`is_admin`) o desactivar **admins** → solo administrador de la plataforma.
  - `PATCH /users/{id}`: solo el propio usuario (hoy cualquiera puede cambiar `active` de cualquiera).
  - `changed_by` del historial sale de `current_user.id`.
- [ ] **Paso 6 – Refresh token** (antes de tener usuarios reales). Tabla propia (hash del token, `user_id`, `expires_at`, `revoked_at`, inicio de la sesión). Dura **10 min** y cada uso lo rota (entrega uno nuevo de 10 min y anula el anterior); sesión de **8 h máximo** aunque se siga renovando. Se envía en cookie `httpOnly` + `Secure` + `SameSite`; el access token va en el cuerpo y el frontend lo guarda solo en memoria. Revocar al cerrar sesión y al desactivar la cuenta. `POST /auth/refresh` y `POST /auth/logout`.
- [ ] **Paso 7 – Límite de intentos de login.** 4 fallos → bloqueo temporal y creciente (p. ej. 1 → 5 → 15 min), contando por IP. Un login correcto reinicia el contador. El mensaje del bloqueo no debe revelar si el email existe.
- [ ] **Paso 8 – Auditoría (obligatoria).** Tabla de auditoría (quién, qué, cuándo, IP): logins correctos y fallidos, bloqueos y todas las acciones del administrador de la plataforma. Solo de inserción, como el historial de citas.
- [ ] **Diseñar cómo se concede `is_platform_admin`:** código de un solo uso, generado en el servidor, con caducidad corta y guardado como hash. Nunca un secreto fijo en código, script del repo o `.env`. Definir quién lo genera y cómo llega a quien lo usa.

**Preguntas abiertas**
- [ ] Límite de intentos: ¿contar por la pareja **IP + cuenta**? Recomendado: 4 fallos de una IP contra una cuenta bloquean solo esa IP para esa cuenta (el atacante no puede bloquear al admin real desde otra IP); además un límite total por IP más alto, y por cuenta solo avisar por email (sin bloquear) si hay muchos fallos desde IPs distintas.
- [ ] Respuesta exacta del login para usuario inactivo (código y mensaje) y en qué consiste el proceso de reactivación por email.

**Recomendado (seguridad de la cuenta de administrador de la plataforma)**
- [ ] Segundo factor (MFA, p. ej. TOTP) para `is_platform_admin`: es la cuenta más valiosa del sistema.

## 🟡 1. Calidad y consistencia

- [ ] CHECK `start_time_before_end_time` sin prefijo de tabla (`availabilities_...`). Requiere migración. Opcional.
- [ ] `.order_by(created_at)` sobrante en `get_by_business` (`App/repositories/appointment.py`): ordenar una sola fila no hace nada.
- [ ] `App/dependencies/__init__.py`: completarlo con todos los `...Dep` o vaciarlo (nadie lo usa).

## 🟢 2. Limpieza

- [ ] `App/routers/business.py`: `limit` por defecto es `5` → `50` como en el resto.
- [ ] Renombrar `service_repository.py` → `service.py` (los demás repositorios no llevan sufijo). Opcional.
- [ ] Renombrar `contexto.md` → `CONTEXTO.md` (o corregir `CLAUDE.local.md`, que lo nombra así).
- [ ] Prefijo `/business` → `/businesses` (opcional).
- [ ] `alembic/README` genérico: borrar o dejar (opcional).
- [ ] `main.py` usa `load_dotenv()` aunque `pydantic-settings` ya lee `.env`. Comprobar si sobra (si se quita, quitar también `python-dotenv` de `requirements.txt`).
- [ ] Configurar Pyright para que use el `venv` (`pyrightconfig.json` con `venvPath`/`venv`); hoy, sin `--pythonpath`, marca `sqlmodel` como no encontrado.
- [ ] Actualizar `contexto.md`: estado (citas y clientes hechos), tabla `customers`, `changed_by` opcional, estructura de `repositories/` (un archivo por entidad), login en curso.

## 🔵 3. Más adelante

- [ ] Endpoint de huecos libres: `GET .../slots?date=...` para el frontend.
- [ ] Vincular cliente con usuario (`customers.user_id`), siempre desde el token, nunca desde el JSON (ver `DECISIONES.md`). Dos casos:
  - **Reserva con sesión iniciada:** el servicio de citas busca un `Customer` del negocio con `user_id` = usuario del token; si no existe, lo crea con ese `user_id`.
  - **Vincular una cuenta a un cliente ya creado** (p. ej. el negocio lo apuntó por teléfono): endpoint tipo "vincular mi cuenta" que compruebe que el email/teléfono coincide y esté verificado (`email_verified_at` / `phone_verified_at`).
- [ ] Notificaciones: interfaz abstracta (`ABC`, como los repositorios) con el **email** como primera implementación (SMTP o servicio externo). SMS y WhatsApp más adelante como implementaciones nuevas, sin tocar los servicios que envían. Lo necesitan la verificación de email, la reactivación de cuentas y los avisos de intentos de login sospechosos.
- [ ] Verificación de email/teléfono del cliente (rellenar `email_verified_at` / `phone_verified_at`); necesaria para vincular cuentas de forma segura.
- [ ] Reactivación de usuarios y clientes por verificación de email (enlace o código de un solo uso, con caducidad). Los negocios solo los reactiva el administrador de la plataforma.
- [ ] Bloqueo `FOR UPDATE` de la cita al cambiar de estado (dos cambios simultáneos podrían leer el mismo estado y "ganar" ambos).
- [ ] Reintento automático si choca el `booking_code` (hoy responde 409 pidiendo reintentar).
- [ ] Tests con pytest (empezar por la lógica pura: `ALLOWED_TRANSITIONS`, `generate_booking_code`, cálculo de `ends_at`, cabe en bloque; luego login y permisos).
- [ ] Restricción de solapamiento de disponibilidades a nivel de base de datos (opcional, avanzado).
- [ ] Pagos (licencia + mantenimiento): tablas futuras.
- [ ] Frontend (React + TypeScript + Vite): empezar con datos falsos y una capa `api/` aislada.

## 🚀 V2 (idea, por revisar)

- [ ] **Negocios públicos:** un negocio se marca como público (p. ej. `businesses.is_public`) y cualquier usuario registrado puede verlo y reservar con él. Da visibilidad a los negocios dentro de la plataforma. Posible función de pago adicional.

---

## ✅ Hecho

**2026-11-23**
- Rutas rotas: historial con `/history` y `response_model` en lista; disponibilidad con `{member_id}` y PATCH con `{availability_id}`; clientes en `/customers`.
- Errores unificados con `response_404` / `response_409`; usuario inactivo → 409; negocio activo comprobado al crear miembros; "no es proveedor" → 409; `active` fuera de los `get` (permite reactivar con PATCH).
- `ServiceService.list_by_business` con 404/409; `UNIQUE_MESSAGES` de miembros sin el CHECK y con mensaje claro del duplicado; código muerto eliminado.
- Servicio de historial: una sola consulta, `response_404("Appointment")` y variable renombrada.
- Paginación estable (`id` como último criterio) en todos los repositorios.
- Precio sin servicios gratuitos: `gt=0` + CHECK `services_price_positive` (migración `8353b73d7dd1`, aplicada).
- `ruff.toml` con F401 activo (`per-file-ignores` para `__init__.py`); exports de `__init__.py` corregidos; formato con `ruff format`.
- `appointment_status` en snake_case; `list_by_member(business_id, member_id)`; `check_phone_number` acepta `None`.
- `requirements.txt` solo con dependencias directas (sin `pymongo` ni `dotenv`); `requirements-dev.txt` con Ruff, Pyright, pytest y httpx.
- Commit de los borrados de `App/core/` y `backend.zip`.
- Merge de `chore/setup-docs-and-cleanup`: `.env.example`, README en inglés, `downgrade` protegido en `188a2956d872`, `DESICIONES.md` → `DECISIONES.md`, `.vscode/settings.json` fuera de Git.
- Flujo completo probado en Scalar (usuarios, negocios, miembros, servicios, disponibilidad, clientes y citas).

**2026-11-20 / 21**
- Imports rotos de `App/repositories/__init__.py` (la app vuelve a arrancar); `CustomerRepository` exportado.
- **Citas – servicio:** condición `ends_at` corregida, cliente buscado en `customers` (negocio + `active`), capacidad con `>=`, `booking_code` `XXX-XXX`, `UNIQUE_MESSAGES` solo con la restricción única, `get` con `get_by_business` (una consulta), `list_by_business` con `offset=0` y sin bloquear negocios inactivos, `update_status` con `ALLOWED_TRANSITIONS` + historial, `update_notes` específico (`notes` obligatorio), orden estable (`starts_at`, `id`).
- **Citas – historial:** `changed_by` opcional (migración `0b9d904842cc` aplicada, `downgrade` protegido), `AppointmentStatusHistoryPublic` acepta `None`, servicio propio con `business_id`, orden estable (`changed_at`, `id`).
- **Citas – conexión:** dependencias `AppointmentServiceDep` y `AppointmentStatusHistoryServiceDep`, routers registrados.
- **Clientes:** repositorio (filtro `active`, orden estable, `changes`), servicio completo (`business_id` y `consent_version` del servidor, regla email/teléfono en PATCH → 422, `UNIQUE_MESSAGES`), dependencia y router registrado.
- `graphify-out/` en `.gitignore`.
