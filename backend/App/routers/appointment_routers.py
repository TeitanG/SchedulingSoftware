from fastapi import APIRouter, Depends
from App.service import (
    create_appointment, search_appointment_by_id, 
    delete_appointments, update_appointment_patch,
    put_appointment, get_all_appointments)
from App.db.schemas import (
    AppointmentCreate, appointment_to_dict, 
    AppointmentPatch, PutAppointment)
from App.repositories import (AppointmentRepository, ServiceRepository,
                            UserRepository)
from App.dependencies import (get_appointment_repository, get_service_repository,
                          get_user_repository)



router = APIRouter(
    prefix= "/appointments",
    tags=["appointment"]
)

@router.get("/")
async def get_appointment(appointment_repo : AppointmentRepository = Depends(get_appointment_repository)):
    appointments = get_all_appointments(appointment_repo)
    return appointments    

@router.get("/{id}")
async def get_appointments_by_id(id: str, appointment_repo : AppointmentRepository = Depends(get_appointment_repository)):
    appointment = get_appointments_by_id(id, appointment_repo)    
    return appointment

@router.post("/")
async def new_appoint(appointment : AppointmentCreate, appointment_repo : AppointmentRepository = Depends(get_appointment_repository)):
    create_appoint =create_appointment(**appointment.model_dump(), appointment_repo = appointment_repo)
    return create_appoint

@router.delete("/{id}")
async def delete_appointment(id : str, appointment_repo : AppointmentRepository = Depends(get_appointment_repository)):
     return delete_appointments(id, appointment_repo)

@router.put("/{id}")
async def update_entire_appointment(id: str, appointment: PutAppointment, appointment_repo :AppointmentRepository = Depends(get_appointment_repository),
                                    service_repo : ServiceRepository= Depends(get_service_repository)):
    update_appointment_put = put_appointment(id, appointment, appointment_repo, service_repo)
    return update_appointment_put

@router.patch("/{id}")
async def update_appointment(id: str, appointment: AppointmentPatch, appointment_repo : AppointmentRepository = Depends(get_appointment_repository),
                             service_repo : ServiceRepository = Depends(get_service_repository), user_repo: UserRepository = Depends(get_user_repository)):
    updated_appointment = update_appointment_patch(id, appointment,appointment_repo, service_repo, user_repo)
    return updated_appointment




