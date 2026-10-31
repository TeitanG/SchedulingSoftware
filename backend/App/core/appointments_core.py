from datetime import datetime, time, timedelta

from bson import ObjectId
from bson.errors import InvalidId


def calculate_end_time(start_hour: datetime, duration: int):

    return start_hour + timedelta(minutes=duration)


def estaDisponible(
    appointment_start: datetime,
    appointment_end: datetime,
    availability_start: time,
    availability_end: time,
) -> bool:

    date = appointment_start.date()

    availability_start_dt = datetime.combine(date, availability_start)
    availability_end_dt = datetime.combine(date, availability_end)

    appointment_start = appointment_start.replace(tzinfo=None)
    appointment_end = appointment_end.replace(tzinfo=None)

    return (
        appointment_start >= availability_start_dt
        and appointment_end <= availability_end_dt
    )


def validar_objectid(id_value: str) -> ObjectId:
    try:
        return ObjectId(id_value)
    except (InvalidId, TypeError):
        raise ValueError("ID invalido")


def validate_entity_exist(collection, object_id, name="entity", filters=None):
    query = {"_id": object_id}

    if filters:
        query.update(filters)

    if not collection.find_one(query):
        raise ValueError(f"{name} no existe")


def revisar_capacidad(capacidad, solapamiento) -> bool:

    return solapamiento < capacidad


def contar_solapamiento(
    appointments, appointment_start, new_end, excluded_id=None
) -> int:

    solapamiento = 0

    for existing in appointments:
        if excluded_id and existing["_id"] == excluded_id:
            continue

        existing_start = existing["appointment_start"]
        existing_end = existing["end_time"]

        if existing_start < new_end and existing_end > appointment_start:
            solapamiento += 1

    return solapamiento


def transiciones_validas():

    transiciones_validas = {
        "pending": {"confirmed", "cancelled"},
        "confirmed": {"completed", "cancelled"},
        "completed": set(),
        "cancelled": set(),
    }
    return transiciones_validas


def validar_transicion_estado(actual, nuevo) -> bool:
    tranciciones = transiciones_validas()

    estados_permitidos = tranciciones.get(actual, set())
    return nuevo in estados_permitidos


def confirmar_cita(actor_rol: str, estado_actual: str) -> str:

    nuevo_estado = "confirmed"

    if not validar_transicion_estado(estado_actual, nuevo_estado):
        raise ValueError("Transicion de estado no permitida")

    if actor_rol not in {"cliente", "proveedor", "administrador"}:
        raise PermissionError("Rol no autorizado para confirmar citas")

    return nuevo_estado


def cancelar_cita(actor_rol: str, estado_actual: str) -> str:
    nuevo_estado = "cancelled"

    if not validar_transicion_estado(estado_actual, nuevo_estado):
        raise ValueError("Transicion de estado no permitida")

    if actor_rol not in {"cliente", "proveedor", "administrador"}:
        raise PermissionError("Rol no autorizado para cancelar la cita")

    return nuevo_estado


def completar_cita(actor_rol: str, estado_actual) -> str:
    nuevo_estado = "completed"

    if not validar_transicion_estado(estado_actual, nuevo_estado):
        raise ValueError("Transicion de estado no permitida")

    if actor_rol not in ({"administrador", "proveedor"}):
        raise PermissionError("Rol no autorizado para cancelar la cita")

    return nuevo_estado
