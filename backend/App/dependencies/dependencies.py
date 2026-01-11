from App.repositories import (MongoDBUserRepository, MongoDBBusinessRepository,
                              MongoDBAppointmentRepository, MongoDBServiceRepository,
                              MongoDBAvailabilityRepository)
from App.db import db_client

def get_user_repository()-> MongoDBUserRepository:
    return MongoDBUserRepository(db_client.users)

def get_business_repository()-> MongoDBBusinessRepository:
    return MongoDBBusinessRepository(db_client.businesses)

def get_appointment_repository() -> MongoDBAppointmentRepository:
    return MongoDBAppointmentRepository(db_client.appointments)

def get_service_repository() -> MongoDBServiceRepository:
    return MongoDBServiceRepository(db_client.services)
 
def get_availability_repository() -> MongoDBAvailabilityRepository:
    return MongoDBAvailabilityRepository(db_client.availabilities)