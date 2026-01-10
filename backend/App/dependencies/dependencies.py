from App.repositories import MongoDBUserRepository, MongoDBBusinessRepository
from App.db import db_client

def get_user_repository()-> MongoDBUserRepository:
    return MongoDBUserRepository(db_client.users)

def get_business_repository()-> MongoDBBusinessRepository:
    return MongoDBBusinessRepository(db_client.business)

def get_appointment_repository():
    pass