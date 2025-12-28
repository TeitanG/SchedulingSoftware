from datetime import time, datetime, timedelta
from bson import ObjectId
from bson.errors import InvalidId


def calculate_end_time(start_hour : datetime,
                       duration : int):
    
    return start_hour + timedelta(minutes=duration)



def estaDisponible(appointment_start : datetime,
                   appointment_end : datetime,
                   availability_start : time,
                   availability_end : time) -> bool:
    
    date = appointment_start.date()

    availability_start_dt = datetime.combine(date, availability_start)
    availability_end_dt = datetime.combine(date, availability_end)

    return(
        appointment_start >= availability_start_dt
        and 
        appointment_end <= availability_end_dt
    )



def validar_objectid(id_value: str) -> ObjectId:
    try:
        return ObjectId(id_value)
    except (InvalidId, TypeError):
        raise ValueError("ID invalido")



def validate_entity_exist(collection, object_id, name="entity") :
    if not collection.find_one({"_id" : object_id}):
        raise ValueError(f"{name} no existe"  )
    
    


def revisar_capacidad(capacidad, solapamiento )-> bool:

    if solapamiento >= capacidad:
        return False
    return True



def contar_solapamiento(appointments, new_start, new_end)->int:
    
    solapamiento = 0

    for existing in appointments:
        existing_start = existing["start_time"]
        existing_end = existing["end_time"]

        if existing_start < new_end and existing_end >new_start:
            solapamiento +=1

    return solapamiento