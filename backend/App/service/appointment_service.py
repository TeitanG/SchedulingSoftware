from datetime import datetime, time
from fastapi import (HTTPException, status, 
                     Response)
from App.core.appointments_core import (contar_solapamiento, estaDisponible,
                                        revisar_capacidad, validar_objectid,
                                        validate_entity_exist, calculate_end_time)
from App.db import db_client
from App.db.models.Appointment import StatusAppointments
from App.db.schemas.appointment_schemas import (appointment_to_dict, AppointmentPatch,PutAppointment)
from App.service.user_service import validar_provider
from App.repositories import (AppointmentRepository, ServiceRepository,
                              UserRepository)


def create_appointment(appointment_start : datetime, 
                       availability_start : time,
                       availability_end : time,
                       provider_id : str,
                       business_id : str,
                       client_id : str,
                       service_id : str,
                       notes : str,
                       appointment_repo : AppointmentRepository):
    

    correct_user= validar_provider(provider_id)
    
    if not correct_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"Error" : "Tipo de usuario incorrecto"})
    

    
    provider_objectid, business_objectid, client_objectid, service_objectid = validar_ids_entidades(
        provider_id, business_id, client_id, service_id
    )   

    
    service = appointment_repo.find_by_id(service_id)

    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= {"Error" : "service no encontrado"})
    
    
    duration = service["duration"]
    capacidad = service["capacity"] 
    
    appointment_end =calculate_end_time(appointment_start, duration)                     

    if not estaDisponible(appointment_end=appointment_end, 
                      appointment_start=appointment_start,
                      availability_end=availability_end,
                      availability_start=availability_start):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= {"mensaje" : "la cita no esta dentro de la disponibilidad"})
    
    
    
    existing_appointments = appointment_repo.find_pending_and_confirmed() 



    solapamiento = contar_solapamiento(
        appointments= existing_appointments,
        new_start = appointment_start,
        new_end = appointment_end
    )

    if not revisar_capacidad(capacidad, solapamiento):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= {"mensaje" : "Horario lleno, por favor elija otro horario"})    
    

    appointments_db = {
        "provider_id" : provider_objectid,
        "client_id" : client_objectid,
        "business_id" : business_objectid,
        "service_id" :service_objectid,
        "start_time" : appointment_start,
        "end_time" : appointment_end,
        "status" : StatusAppointments.pending,
        "notes" : notes
    }


    id = appointment_repo.save(appointments_db)
    new_appointment = appointment_repo.find_by_id(id)
    return appointment_to_dict(new_appointment)
    
def validar_ids_entidades(provider_id : str,
                      business_id : str,
                      client_id : str,
                      service_id : str,                      
                      ):
    try:
        provider_objectid = validar_objectid(provider_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"mensaje": f"Proveedor: {str(e)}"})

    try:
        business_objectid = validar_objectid(business_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"mensaje": f"Business: {str(e)}"})
    
    try:
        client_objectid = validar_objectid(client_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"mensaje": f"Cliente: {str(e)}"})
    
    try:
        service_objectid = validar_objectid(service_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"mensaje": f"Servicio: {str(e)}"})
    
    return provider_objectid, business_objectid, client_objectid, service_objectid    

def get_all_appointments(appointment_repo : AppointmentRepository):
    appointments = appointment_repo.find_all()
    if not appointments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"Error" : "No appointment found"})
    
    appointment_list = list(appointments)
    
    return appointment_list

def search_appointment_by_id(id: str, appointment_repo: AppointmentRepository):
        
        appointment = appointment_repo.find_by_id(id)
        if not appointment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                 detail={"Error" : "Appointment Not found"})
        return appointment_to_dict(appointment)
    

def delete_appointments(id: str, appointment_repo : AppointmentRepository):
    
    appointment_deleted = appointment_repo.delete(id)
        
    if not appointment_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail={"error" : "Appointment not found"})
        
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def update_appointment_patch(
    appointment_id: str,
    data: AppointmentPatch,
    appointment_repo : AppointmentRepository,
    service_repo: ServiceRepository,
    user_repo : UserRepository
):
    try:
        appointment_objectid = validar_objectid(appointment_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    current_appointment = appointment_repo.find_by_id(appointment_id)



    if not current_appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    updated_data = {
        k: v for k, v in data.model_dump().items() if v is not None
    }

    provider_id = updated_data.get(
        "provider_id", current_appointment["provider_id"]
    )
    business_id = updated_data.get(
        "business_id", current_appointment["business_id"]
    )
    client_id = updated_data.get(
        "client_id", current_appointment["client_id"]
    )
    service_id = updated_data.get(
        "service_id", current_appointment["service_id"]
    )

    provider_objectid, business_objectid, client_objectid, service_objectid = (
        validar_ids_entidades(
            provider_id=provider_id,
            business_id=business_id,
            client_id=client_id,
            service_id=service_id
        )
    )

    updated_data.update({
        "provider_id": provider_objectid,
        "business_id": business_objectid,
        "client_id": client_objectid,
        "service_id": service_objectid
    })

    service = service_repo.find_by_id(service_id)
    provider = user_repo.find_by_id(provider_id)

    if not service:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Service not found"
        )

    if not provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provider not found"
        )

    duration = service["duration"]
    capacidad = service["capacidad"]
    availability_start = provider["availability_start"]
    availability_end = provider["availability_end"]

    appointment_start = updated_data.get(
        "appointment_start",
        current_appointment["appointment_start"]
    )

    appointment_end = calculate_end_time(appointment_start, duration)

    updated_data["appointment_end"] = appointment_end
    updated_data["duration"] = duration

    if not estaDisponible(
        appointment_start=appointment_start,
        appointment_end=appointment_end,
        availability_start=availability_start,
        availability_end=availability_end
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La cita no está dentro de la disponibilidad"
        )

    existing_appointments = appointment_repo.existing_appointments(provider_id, business_id)

    solapamiento = contar_solapamiento(
        appointments=existing_appointments,
        new_start=appointment_start,
        new_end=appointment_end
    )

    if not revisar_capacidad(capacidad, solapamiento):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Horario lleno, por favor elija otro horario"
        )

    sucess = appointment_repo.update(appointment_id, updated_data)
    if not sucess:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"Appointment not saved"})

    return {
        "message": "Appointment updated successfully",
        "appointment_id": appointment_to_dict(appointment_objectid)
    }


def put_appointment(id:str, data:PutAppointment, appointment_repo : AppointmentRepository,
                    service_repo : ServiceRepository):   
    
    current_appointment = appointment_repo.find_by_id(id)

    if not current_appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail={"Mensaje": "Cita no encontrada"})           
    
    full_data = {
        "appointment_start" : data.appointment_start,        
        "provider_id": data.provider_id,
        "business_id": data.business_id,
        "client_id": data.client_id,
        "service_id": data.service_id,
        "notes": data.notes,
        "status" : data.notes        
    }

    provider_id,business_id,client_id,service_id=(
        validar_ids_entidades(
            provider_id=full_data["provider_id"],
            business_id=full_data["business_id"],
            service_id=full_data["service_id"],
            client_id=full_data["client_id"]    ,        
        )
    )

    service = service_repo.find_by_id(str(service_id))

    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail={"Error" : "Servicio no encontrado"})

    duration = service["duration"]   

    end_time = calculate_end_time(full_data["appointment_start"], duration)  

    full_data["end_time"] = end_time
    
    full_data.update({
        "provider_id": provider_id,
        "business_id":business_id,
        "service_id": service_id,
        "client_id": client_id        
    })

    sucess = appointment_repo.update(id, full_data)

    if not sucess:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"Error" : "Appointment not updated"})

    updated_appointment = appointment_repo.find_by_id(id)
    if not updated_appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"Error" : "Appointment saved but not found"})

    return{        
        "Message": "Cita actualizada",
        "updated": appointment_to_dict(updated_appointment)
    }  