from datetime import datetime, time
from App.core.appointments_core import contar_solapamiento, estaDisponible, revisar_capacidad, validar_objectid, validate_entity_exist, calculate_end_time
from fastapi import HTTPException, status, Response
from App.db import db_client
from App.db.models.Appointment import status_appointments
from App.db.schemas.appointment_schemas import appointment_to_dict




def create_appointment(appointment_start : datetime, 
                       availability_start : time,
                       availability_end : time,
                       duration : int,
                       provider_id : str,
                       business_id : str,
                       capacidad : int,
                       client_id : str,
                       service_id : str,
                       notes : str):
    
    appointment_end =calculate_end_time(appointment_start, duration )                     

    if not estaDisponible(appointment_end=appointment_end, 
                      appointment_start=appointment_start,
                      availability_end=availability_end,
                      availability_start=availability_start):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= {"mensaje" : "la cita no esta dentro de la disponibilidad"})
    
    existing_appointments = list(db_client.appointments.find({
        "provider_id" : provider_id,
        "business_id" : business_id,
        "status" : {"$in": ["Pendiente", "Confirmado"]}
    }))
    
    solapamiento = contar_solapamiento(
        appointments= existing_appointments,
        new_start = appointment_start,
        new_end = appointment_end
    )

    if not revisar_capacidad(capacidad, solapamiento):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= {"mensaje" : "Horario lleno, por favor elija otro horario"})
    
    try:
        provider_objectid = validar_objectid(provider_id)
        validate_entity_exist(db_client.providers, provider_objectid, "Proveedor")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"mensaje": f"Proveedor: {str(e)}"})

    try:
        business_objectid = validar_objectid(business_id)
        validate_entity_exist(db_client.businesses, business_objectid, "Business")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"mensaje": f"Business: {str(e)}"})
    
    try:
        client_objectid = validar_objectid(client_id)
        validate_entity_exist(db_client.providers, client_id, "Cliente")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"mensaje": f"Cliente: {str(e)}"})
    
    try:
        service_objectid = validar_objectid(service_id)
        validate_entity_exist(db_client.providers, service_objectid, "Servicio")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"mensaje": f"Servicio: {str(e)}"})
    

    appointments_db = {
        "provider_id" : provider_objectid,
        "client_id" : client_objectid,
        "business_id" : business_objectid,
        "service_id" :service_objectid,
        "start_time" : appointment_start,
        "end_time" : appointment_end,
        "duration" : duration,
        "status" : status_appointments.pending,
        "notes" : notes
    }


    id = db_client.appointments.insert_one(appointments_db).inserted_id
    new_appointment = db_client.appointments.find_one({"_id": id})
    return appointment_to_dict(new_appointment)
    


def serch_appointment(field: str, key):
    if field == "_id":
        try:
            key =validar_objectid(key)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"Error": "User not found"})
        appointment = db_client.appointments.find_one({field : key})
        if not appointment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"Error" : "User Not found"})
        return appointment_to_dict(appointment)
    

def delete_appointments(field: str, key):
    if field =="_id":
        try:
            key = validar_objectid(key)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"Error" : "appointment not found"})
        
        appointment_deleted = db_client.appointments.find_one_and_delete({field : key})
        
        if not appointment_deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error" : "Appointment not found"})
        
    return Response(status_code=status.HTTP_204_NO_CONTENT)

        
        