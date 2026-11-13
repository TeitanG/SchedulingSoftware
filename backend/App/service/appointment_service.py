from typing import Any

from fastapi import HTTPException, Response, status

from App.core import (
    calculate_end_time,
    contar_solapamiento,
    estaDisponible,
    revisar_capacidad,
    validar_objectid,
)
from App.core.availability_core import time_from_db
from App.db.models import StatusAppointments
from App.db.schemas import (
    AppointmentCreate,
    AppointmentPatch,
    PutAppointment,
    appointment_to_dict,
    appointments_to_dict,
)
from App.repositories import (
    AppointmentRepository,
    AvailabilityRepository,
    ServiceRepository,
    UserRepository,
)

day_map = {
    0: "monday",
    1: "tuesday",
    2: "wednesday",
    3: "thursday",
    4: "friday",
    5: "saturday",
    6: "sunday",
}


class AppointmentService:
    def __init__(
        self,
        appointment_repo: AppointmentRepository,
        user_repo: UserRepository,
        service_repo: ServiceRepository,
        availability_repo: AvailabilityRepository,
    ):
        self.appointment_repo = appointment_repo
        self.user_repo = user_repo
        self.service_repo = service_repo
        self.availability_repo = availability_repo

    def create_appointment(self, data: AppointmentCreate):

        appointment_day = day_map[data.appointment_start.weekday()]

        provider_objectid, business_objectid, client_objectid, service_objectid = (
            validar_ids_entidades(
                data.provider_id, data.business_id, data.client_id, data.service_id
            )
        )

        service = self.service_repo.find_by_id(data.service_id)

        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"Error": "service no encontrado"},
            )

        provider = self.user_repo.find_by_id(data.provider_id)
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"Error": "Provider not found"},
            )

        availability = self.availability_repo.find_by_provider(data.provider_id)

        if not availability:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"Error": "Availability not found"},
            )

        matching_availability = next(
            (a for a in availability if a.get("day") == appointment_day), None
        )
        if not matching_availability:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "Error": f"El proveedor no tiene disponibilidad los dias {appointment_day}"
                },
            )

        availability_start = time_from_db(matching_availability["start_time"])
        availability_end = time_from_db(matching_availability["end_time"])

        duration = service["duration"]
        capacidad = service["capacity"]

        appointment_end = calculate_end_time(data.appointment_start, duration)

        if not estaDisponible(
            appointment_end=appointment_end,
            appointment_start=data.appointment_start,
            availability_end=availability_end,
            availability_start=availability_start,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"mensaje": "la cita no esta dentro de la disponibilidad"},
            )

        existing_appointments = self.appointment_repo.find_pending_and_confirmed(
            business_id=data.business_id, provider_id=data.provider_id
        )

        solapamiento = contar_solapamiento(
            appointments=existing_appointments,
            appointment_start=data.appointment_start,
            new_end=appointment_end,
        )

        if not revisar_capacidad(capacidad, solapamiento):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"mensaje": "Horario lleno, por favor elija otro horario"},
            )

        appointments_db = {
            "provider_id": provider_objectid,
            "client_id": client_objectid,
            "business_id": business_objectid,
            "service_id": service_objectid,
            "appointment_start": data.appointment_start,
            "end_time": appointment_end,
            "status": StatusAppointments.pending.value,
            "notes": data.notes,
        }

        id = self.appointment_repo.save(appointments_db)
        new_appointment = self.appointment_repo.find_by_id(id)
        return appointment_to_dict(new_appointment)

    def delete_appointments(self, id: str):

        appointment_deleted = self.appointment_repo.delete(id)

        if not appointment_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Appointment not found"},
            )

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    def update_appointment_patch(self, appointment_id: str, data: AppointmentPatch):

        try:
            appointment_objectid = validar_objectid(appointment_id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        current_appointment = self.appointment_repo.find_by_id(
            str(appointment_objectid)
        )

        if not current_appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found"
            )

        updated_data = {k: v for k, v in data.model_dump().items() if v is not None}

        provider_id = updated_data.get(
            "provider_id", str(current_appointment["provider_id"])
        )
        business_id = updated_data.get(
            "business_id", str(current_appointment["business_id"])
        )
        client_id = updated_data.get("client_id", str(current_appointment["client_id"]))
        service_id = updated_data.get(
            "service_id", str(current_appointment["service_id"])
        )

        provider_objectid, business_objectid, client_objectid, service_objectid = (
            validar_ids_entidades(
                provider_id=provider_id,
                business_id=business_id,
                client_id=client_id,
                service_id=service_id,
            )
        )

        availability = self.availability_repo.find_by_provider(provider_id)
        if not availability:
            raise HTTPException(status_code=404, detail="Availability not found")

        appointment_start = updated_data.get(
            "appointment_start", current_appointment["appointment_start"]
        )

        appointment_day = day_map[appointment_start.weekday()]

        matching_availability = next(
            (a for a in availability if a.get("day") == appointment_day), None
        )

        if not matching_availability:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "Error": f"El proveedor no tiene disponibilidad los dias {appointment_day}"
                },
            )
        availability_start = time_from_db(matching_availability["start_time"])
        availability_end = time_from_db(matching_availability["end_time"])

        updated_data.update(
            {
                "provider_id": provider_objectid,
                "business_id": business_objectid,
                "client_id": client_objectid,
                "service_id": service_objectid,
            }
        )

        service = self.service_repo.find_by_id(service_id)
        provider = self.user_repo.find_by_id(provider_id)

        if not service:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Service not found"
            )

        if not provider:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Provider not found"
            )

        duration = service["duration"]
        capacidad = service["capacity"]

        appointment_end = calculate_end_time(appointment_start, duration)

        updated_data["end_time"] = appointment_end
        updated_data["duration"] = duration

        if not estaDisponible(
            appointment_end=appointment_end,
            appointment_start=appointment_start,
            availability_end=availability_end,
            availability_start=availability_start,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La cita no está dentro de la disponibilidad",
            )

        existing_appointments = self.appointment_repo.existing_appointments(
            provider_id, business_id
        )

        solapamiento = contar_solapamiento(
            appointments=existing_appointments,
            appointment_start=appointment_start,
            new_end=appointment_end,
            excluded_id=appointment_id,
        )

        if not revisar_capacidad(capacidad, solapamiento):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Horario lleno, por favor elija otro horario",
            )

        sucess = self.appointment_repo.update(appointment_id, updated_data)
        if not sucess:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"Error": "Appointment not saved"},
            )

        updated = self.appointment_repo.find_by_id(appointment_id)

        return {
            "message": "Appointment updated successfully",
            "appointment": appointment_to_dict(updated),
        }

    def put_appointment(self, id: str, data: PutAppointment):

        current_appointment = self.appointment_repo.find_by_id(id)
        if not current_appointment:
            raise HTTPException(
                status_code=404, detail={"Mensaje": "Cita no encontrada"}
            )

        # Preserva el status actual
        status_value = current_appointment.get("status")
        if isinstance(status_value, StatusAppointments):
            status_value = status_value.value

        # Valida los ObjectIds
        provider_id, business_id, client_id, service_id = validar_ids_entidades(
            data.provider_id, data.business_id, data.client_id, data.service_id
        )

        # Obtiene el servicio para duration y capacity
        service = self.service_repo.find_by_id(str(service_id))
        if not service:
            raise HTTPException(
                status_code=404, detail={"Error": "Servicio no encontrado"}
            )

        duration = service["duration"]
        capacidad = service["capacity"]
        appointment_end = calculate_end_time(data.appointment_start, duration)

        # Valida disponibilidad del proveedor
        appointment_day = day_map[data.appointment_start.weekday()]
        availability = self.availability_repo.find_by_provider(data.provider_id)

        matching_availability = next(
            (a for a in availability if a.get("day") == appointment_day), None
        )
        if not matching_availability:
            raise HTTPException(
                status_code=400,
                detail={
                    "Error": f"El proveedor no tiene disponibilidad los días {appointment_day}"
                },
            )

        if not estaDisponible(
            appointment_start=data.appointment_start,
            appointment_end=appointment_end,
            availability_start=time_from_db(matching_availability["start_time"]),
            availability_end=time_from_db(matching_availability["end_time"]),
        ):
            raise HTTPException(
                status_code=400, detail={"Error": "Fuera del horario disponible"}
            )

        # Valida solapamiento excluyendo la cita actual
        existing_appointments = self.appointment_repo.existing_appointments(
            data.provider_id, data.business_id
        )
        solapamiento = contar_solapamiento(
            appointments=existing_appointments,
            appointment_start=data.appointment_start,
            new_end=appointment_end,
            excluded_id=id,  # ← excluye la cita que se está actualizando
        )
        if not revisar_capacidad(capacidad, solapamiento):
            raise HTTPException(status_code=400, detail={"Error": "Horario lleno"})

        full_data = {
            "appointment_start": data.appointment_start,
            "end_time": appointment_end,
            "provider_id": provider_id,
            "business_id": business_id,
            "client_id": client_id,
            "service_id": service_id,
            "notes": data.notes,
            "status": status_value,
        }

        success = self.appointment_repo.update(id, full_data)
        if not success:
            raise HTTPException(
                status_code=404, detail={"Error": "Appointment not updated"}
            )

        updated = self.appointment_repo.find_by_id(id)
        return {"Message": "Cita actualizada", "updated": appointment_to_dict(updated)}


def validar_ids_entidades(
    provider_id: str,
    business_id: str,
    client_id: str,
    service_id: str,
):
    try:
        provider_objectid = validar_objectid(provider_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"mensaje": f"Proveedor: {e!s}"},
        )

    try:
        business_objectid = validar_objectid(business_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"mensaje": f"Business: {e!s}"},
        )

    try:
        client_objectid = validar_objectid(client_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"mensaje": f"Cliente: {e!s}"},
        )

    try:
        service_objectid = validar_objectid(service_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"mensaje": f"Servicio: {e!s}"},
        )

    return provider_objectid, business_objectid, client_objectid, service_objectid


def get_all_appointments(appointment_repo: AppointmentRepository):
    appointments = appointment_repo.find_all()
    if not appointments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"Error": "No appointment found"},
        )

    appointment_list = list(appointments)

    return appointments_to_dict(appointment_list)


def search_appointment_by_id(
    id: str, appointment_repo: AppointmentRepository
) -> dict[str, Any]:

    appointment = appointment_repo.find_by_id(id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"Error": "Appointment Not found"},
        )
    return appointment_to_dict(appointment)
