# TODO — SchedulingSoftware (backend)

Lista de lo que falta por hacer. Última revisión: 2026-11-21.
Marca con `[x]` lo que vayas terminando. Las decisiones y su motivo van en `DESICIONES.md`; el contexto general, en `contexto.md`.

Al terminar cada bloque: `pyright --pythonpath .\venv\Scripts\python.exe App`, `ruff check App`, `ruff format App` y probar en `/scalar` que **todas** las rutas aparecen con los parámetros correctos (path, no query).

---

## 🔴 1. Rompen endpoints (hacer primero)

- [ ] **Historial: `response_model` de un objeto, pero devuelve una lista** (`App/routers/appointment_history.py`, línea 18).
  `response_model=AppointmentStatusHistoryPublic` y la función devuelve `list[...]` → FastAPI no puede validar la respuesta → **500 siempre** (incluso con `[]`). Debe ser `list[AppointmentStatusHistoryPublic]`. DONE
- [ ] **Historial: ruta sin `/history`** (mismo archivo, líneas 13 y 18).
  Hoy queda `GET .../appointments/{appointment_id}/`, que solo se diferencia de "obtener la cita" (`GET .../appointments/{appointment_id}`) por la barra final. Usar `"/history"`. DONE
- [ ] **Disponibilidad: `members_id` ≠ `{member_id}`** (`App/routers/availability.py`, línea 26). 
  FastAPI no los relaciona y convierte `members_id` en **query obligatorio** → `POST .../availabilities/` da 422. El nombre del parámetro debe coincidir exactamente con el del prefix. (Además, la variable `Service` con mayúscula → `service`.)DONE
- [ ] **Disponibilidad: PATCH sin `{availability_id}` en la ruta** (mismo archivo, línea 56).
  `@router.patch("/")` → el id viaja como `?availability_id=`. Debe ser `"/{availability_id}"`, como el resto de PATCH. Falta también `-> Availability`. DONE

## 🟠 2. Comportamiento incorrecto

- [ ] **`ServiceService.list_by_business`** (`App/service/service.py`, líneas 85-91): negocio inexistente → 409 (debe ser **404**); inactivo → `401` sin `detail` (401 es "no autenticado"). Mismo bug ya arreglado en clientes. Decidir si se bloquea el listado de un negocio inactivo (en citas se decidió que no). DONE
- [ ] **`BusinessMemberService.UNIQUE_MESSAGES`** (`App/service/business_member.py`, línea 19): incluye `business_member_has_role`, que es un **CHECK** (va contra la regla) y además el nombre real es `business_members_has_role` → nunca se usa. Quitarlo. Mejorar el mensaje del duplicado ("This user is already a member of this business"). Done
- [ ] **`BusinessMemberService.create`** (líneas 45-56): usuario inactivo → 404 "User Not found" (inactivo debe ser **409**; 404 es "no existe"). No comprueba si el negocio está activo (servicios, clientes y citas sí). DONE
- [ ] **Precio: Pydantic y Postgres no dicen lo mismo** (`App/db/models/service.py`, líneas 14, 30, 72): `gt=0` en Pydantic vs `CHECK price_amount >= 0`. Decidir si existen servicios gratuitos: si sí → `ge=0` en `ServiceBase` **y** `ServiceUpdate`; si no → migración para el CHECK. Anotar en `DESICIONES.md`. DONE. Lo deje sin servicios gratuitos
- [ ] **Prefix de clientes en singular** (`App/routers/customer.py`, línea 14): `/customer` → `/customers`, como el resto. DONE
- [ ] **Servicio de historial consulta dos veces** (`App/service/appointment_history.py`): el `self.appointments.get(...)` + su `if` sobran; `get_by_business` ya devuelve `None` si no existe **o** es de otro negocio. Dejar solo `get_by_business` y un `if`. La variable `service` contiene una cita → renombrar. Quitar el import de `ServiceRepository` (línea 8). Done

## 🟡 3. Calidad y consistencia

- [ ] **Código muerto:** `if ... is None` después de `self.get(...)` en `App/service/service.py` (línea ~63) y `App/service/business_member.py` (línea ~79, además con mensaje "Business not found"). Done
- [ ] **Paginación inestable** (añadir `id` como último criterio de `order_by`): `user.py` (`name`, se repite), `business_member.py` (`created_at`), `provider_service.py` (`created_at`), `availability.py` (`day, start_time`). DONE
- [ ] **`ruff.toml` ignora F401 en todo el proyecto** → no se detectan imports sin usar. Activarlo y usar `[lint.per-file-ignores]` solo para los `__init__.py`. Quitar el `# noqa: F401` sobrante de `scripts/print_ddl.py` (RUF100). DONE
- [ ] **Exports en `__init__.py`:** `App/repositories/__init__.py` exporta `ProviderService` (el **modelo**) en vez de `ProviderServiceRepository`; `App/dependencies/__init__.py` exporta `UserService` (la clase del servicio, no una dependencia) y le faltan casi todos los `...Dep` → completarlo o vaciarlo (nadie lo usa). DONE 
- [ ] **Formato:** `ruff format App` (4 archivos: `models/availability.py`, `models/user.py`, `repositories/__init__.py`, `repositories/service_repository.py`). DONE
- [ ] `CustomerCreate.check_phone_number` (`App/db/models/customer.py`, línea 103): el retorno ya es `str | None`, pero el parámetro sigue siendo `value: str` → `str | None`. Done
- [ ] Query param `appointmentStatus` en camelCase (`App/routers/appointment.py`, línea 37) → `appointment_status` (no `status`: taparía el `status` de FastAPI). Done
- [ ] `AvailabilityService.list_by_member(member_id, business_id)` recibe los ids al revés que `get`/`create`/`update` → `business_id` primero o argumentos por nombre. DONE
- [ ] "No es proveedor": 422 en disponibilidad y proveedor-servicio, 409 en citas → unificar (encaja mejor 409: es un estado guardado). DONE
- [ ] Mensajes con mayúsculas raras: "Business not Found", "Business Not active", "User Not found". DONE
- [ ] CHECK `start_time_before_end_time` sin prefijo de tabla (`availabilities_...`). Requiere migración. Opcional.

## 🟢 4. Limpieza

- [x] Borrar el código antiguo de Mongo: `App/core/` (borrado en disco; falta commit).
- [ ] Hacer commit de los borrados (`App/core/`, `backend.zip`).
- [ ] `requirements.txt`: quitar `pymongo` (ya nadie usa `bson`); separar `ruff`/`pyright` en `requirements-dev.txt`.
- [ ] `App/routers/business.py`: `limit` por defecto es `5` → `50` como en el resto.
- [ ] Renombrar `service_repository.py` → `service.py` (los demás repositorios no llevan sufijo). Opcional.
- [ ] Renombrar `DESICIONES.md` → `DECISIONES.md` y `contexto.md` → `CONTEXTO.md` (o corregir `CLAUDE.md`, que los nombra así).
- [ ] Prefijo `/business` → `/businesses` (opcional).
- [ ] `alembic/README` genérico: borrar o dejar (opcional).
- [ ] `main.py` usa `load_dotenv()` aunque `pydantic-settings` ya lee `.env`. Comprobar si sobra.
- [ ] Configurar Pyright para que use el `venv` (`pyrightconfig.json` con `venvPath`/`venv`); hoy, sin `--pythonpath`, marca `sqlmodel` como no encontrado.
- [ ] Actualizar `contexto.md`: estado (citas y clientes hechos), tabla `customers`, `changed_by` opcional, estructura de `repositories/` (un archivo por entidad, ya no `repositories.py` + `sql_repositories.py`).
- [ ] Probar todo el flujo de citas en Scalar: crear (capacidad, disponibilidad, medianoche, pasado), cambiar estado (transiciones válidas e inválidas), notas (`{}` → 422, `null` borra), historial.

## 🔵 5. Más adelante

- [ ] Endpoint de huecos libres: `GET .../slots?date=...` para el frontend.
- [ ] Login y permisos (JWT). El actor nunca viene del cuerpo; `changed_by` del historial sale del usuario autenticado. Hoy cualquiera puede cambiar `active` de usuarios, etc.
- [ ] Vincular cliente con usuario (`customers.user_id`), siempre desde el token, nunca desde el JSON (ver `DESICIONES.md`). Dos casos:
  - **Reserva con sesión iniciada:** el servicio de citas busca un `Customer` del negocio con `user_id` = usuario del token; si no existe, lo crea con ese `user_id`.
  - **Vincular una cuenta a un cliente ya creado** (p. ej. el negocio lo apuntó por teléfono): endpoint tipo "vincular mi cuenta" que compruebe que el email/teléfono coincide y esté verificado (`email_verified_at` / `phone_verified_at`).
- [ ] Verificación de email/teléfono del cliente (rellenar `email_verified_at` / `phone_verified_at`); necesaria para vincular cuentas de forma segura.
- [ ] Bloqueo `FOR UPDATE` de la cita al cambiar de estado (dos cambios simultáneos podrían leer el mismo estado y "ganar" ambos).
- [ ] Reintento automático si choca el `booking_code` (hoy responde 409 pidiendo reintentar).
- [ ] Tests con pytest (empezar por la lógica pura: `ALLOWED_TRANSITIONS`, `generate_booking_code`, cálculo de `ends_at`, cabe en bloque).
- [ ] Restricción de solapamiento de disponibilidades a nivel de base de datos (opcional, avanzado).
- [ ] Pagos (licencia + mantenimiento): tablas futuras.
- [ ] Frontend (React + TypeScript + Vite): empezar con datos falsos y una capa `api/` aislada.

---

## ✅ Hecho (2026-11-20 / 21)

- Imports rotos de `App/repositories/__init__.py` (la app vuelve a arrancar); `CustomerRepository` exportado.
- **Citas – servicio:** condición `ends_at` corregida, cliente buscado en `customers` (negocio + `active`), capacidad con `>=`, `booking_code` `XXX-XXX`, `UNIQUE_MESSAGES` solo con la restricción única, `get` con `get_by_business` (una consulta), `list_by_business` con `offset=0` y sin bloquear negocios inactivos, `update_status` con `ALLOWED_TRANSITIONS` + historial, `update_notes` específico (`notes` obligatorio), orden estable (`starts_at`, `id`).
- **Citas – historial:** `changed_by` opcional (migración `0b9d904842cc` aplicada, `downgrade` protegido), `AppointmentStatusHistoryPublic` acepta `None`, servicio propio con `business_id`, orden estable (`changed_at`, `id`).
- **Citas – conexión:** dependencias `AppointmentServiceDep` y `AppointmentStatusHistoryServiceDep`, routers registrados.
- **Clientes:** repositorio (filtro `active`, orden estable, `changes`), servicio completo (`business_id` y `consent_version` del servidor, regla email/teléfono en PATCH → 422, `UNIQUE_MESSAGES`), dependencia y router registrado.
- `graphify-out/` en `.gitignore`.
