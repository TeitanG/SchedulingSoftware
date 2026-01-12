from bson import ObjectId
from typing import Optional, Dict, Any, List
from App.repositories import (UserRepository, BusinessRepository,
                              ServiceRepository, AppointmentRepository, AvailabilityRepository)
from datetime import datetime

from App.db.models import user_Status, user_Type, BusinessType
from backend.App.db.models.availability import daysOfTheWeek



class MongoDBUserRepository(UserRepository):
    def __init__(self, collection):
        self.collection = collection
    
    def find_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        try:
            return self.collection.find_one({"_id": ObjectId(entity_id)})
        except:
            return None
    
    def find_one(self, query: Dict) -> Optional[Dict[str, Any]]:
        return self.collection.find_one(query)
    
    def find_all(self, query: Optional[Dict] = None) -> List[Dict[str, Any]]:
        if query:
            return list(self.collection.find(query))
        return list(self.collection.find())
    
    def find_by_role(self, role: user_Type) -> List[Dict[str, Any]]:
        return list(self.collection.find({"user_type": role.value}))   
    
    
    def save(self, entity: Dict[str, Any]) -> str:
        result = self.collection.insert_one(entity)        
        return str(result.inserted_id)
    
    def update(self, entity_id: str, data: Dict[str, Any]) -> bool:
        result = self.collection.update_one(
            {"_id": ObjectId(entity_id)},
            {"$set": data}
        )
        return result.modified_count > 0
    
    def delete(self, entity_id: str) -> bool:
        result = self.collection.delete_one({"_id": ObjectId(entity_id)})
        return result.deleted_count > 0
    
    def find_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        return self.collection.find_one({"username": username})
    
    def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        return self.collection.find_one({"email": email})
    
    def find_by_status(self, status: user_Status) -> List[Dict[str, Any]]:
        return list(self.collection.find({"user_status": status.value}))

 
class MongoDBBusinessRepository(BusinessRepository):
        
    def __init__(self, collection):
        self.collection = collection

    
    def find_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        try:
            return self.collection.find_one({"_id": ObjectId(entity_id)})
        except Exception:
            return None
        
    def find_one(self, query: Dict[str, Any])-> Optional[Dict[str, Any]]:
        return self.collection.find_one(query)
    
    def find_all(self, query: Optional[Dict[str, Any]]= None) -> List[Dict[str, Any]]:
        if query:
            return list(self.collection.find(query))
        return list(self.collection.find())   
       
    def save(self, entity: Dict[str, Any]) -> str:
        result = self.collection.insert_one(entity)
        return str(result.inserted_id)
    
    def update(self, entity_id: str, data: Dict[str, Any])->bool:
        try:
            result = self.collection.update_one(
                {"_id":ObjectId(entity_id)},
                {"$set":data}
            )
            return result.modified_count >0
        except Exception:
            return False
        
    def delete(self, entity_id: str):
        try:
            result = self.collection.delete_one({"_id": ObjectId(entity_id)})
            return result.deleted_count > 0
        except Exception:
            return False
        
    
    def find_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        return self.collection.find_one({"name":name})
    
    def find_by_type(self, business_type: BusinessType) -> List[Dict[str, Any]]:
        return list(self.collection.find({"business_type": business_type}))
    
    def find_active(self) -> List[Dict[str, Any]]:
        return list(self.collection.find({"active": True}))
    



class MongoDBAppointmentRepository(AppointmentRepository):
    def __init__(self, collection):
        self.collection = collection

    def find_by_id(self, entity_id: str) -> Optional[Dict[str,Any]]:
        try:
            return self.collection.find_one({"_id": ObjectId(entity_id)})
        except Exception:
            return None
        
    def find_one(self, query: Dict[str,Any])-> Optional[Dict[str, Any]]:
        return self.collection.find_one(query)
    
    def find_all(self, query: Optional[Dict[str, Any]]= None) -> List[Dict[str, Any]]:
        if query:
            return list(self.collection.find(query))
        return list(self.collection.find())
    
    def update(self, entity_id: str, data: Dict[str, Any])->bool:
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(entity_id)},
                {"$set": data}
            ) 
            return result.modified_count > 0
        except Exception:
            return False
        
    def delete(self, entity_id: str) -> bool:
        try:
            result = self.collection.delete_one({"_id": ObjectId(entity_id)})
            return result > 0
        except Exception:
            return False
        
    def find_by_status(self, status: user_Status) -> List[Dict[str, Any]]:
        return list(self.collection.find({"user_status" : status.value}))
        

    def find_by_provider(self, provider_id: str, date_range: Optional[tuple[datetime, datetime]] =None ) -> List[Dict[str, Any]]:
        try:
            provider_oid = ObjectId(provider_id)
            query:dict[str,Any]  = {"provider_id": provider_oid}
            
            if date_range:
                start_date, end_date = date_range
                query["start_time"] = {"$gte": start_date, "$lte":end_date}
            
            return list(self.collection.find(query).sort("start_time", 1))
        except Exception:
            return []
        
    def find_by_client(self, client_id: str, date_range: Optional[tuple[datetime, datetime]] = None) -> List[Dict[str, Any]]:
        try:
            client_oid = ObjectId(client_id)
            query:dict[str, Any] = {"provider_id": client_oid}

            if date_range:
                start_date, end_date = date_range
                query["start_time"] = {"$gte": start_date, "$lte":end_date}
            return list(self.collection.find(query).sort("start_time", 1))
        except Exception:
            return []
        
    def save(self, entity: Dict[str, Any]) -> str:
        result = self.collection.insert_one(entity)
        return result(result.inserted_one)

    def find_overlapping(self, provider_id: str, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        try:
            provider_oid = ObjectId(provider_id)
            query = {
                "provider_id" : provider_oid,
                "start_time" : {"$lt":end_time},
                "end_time" : {"get": start_time}
            }
            appointments= list(self.collection.find(query))

            appointments.sort(key=lambda x: x.get("start_time", datetime.min))
            return appointments
        except Exception:
            return[]
        
            
    def find_pending_and_confirmed(self) -> List[Dict[str, Any]]:
        return super().find_pending_and_confirmed()
  

class MongoDBServiceRepository(ServiceRepository):
    def __init__(self, collection):
        self.collection =collection
    
    def find_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        try:
            return self.collection.find_one({"_id", ObjectId(entity_id)})
        except Exception:
            return None
        
    def find_one(self, query: Dict[str, Any])-> Optional[Dict[str, Any]]:
        return self.collection.find_one(query)
    
    def find_all(self, query: Optional[Dict[str, Any]]= None)-> List[Dict[str, Any]]:
        if query:
            return list(self.collection.find(query))
        return list(self.collection.find())
    
    def update(self, entity_id: str, data: Dict[str, Any]) -> bool:
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(entity_id)},
                {"$set": data}
                
            )
            return result.modified_count >0
        except Exception:
            return False
        
    def delete(self, entity_id:str)-> bool:
        try:
            result= self.collection.delete_one({"_id": ObjectId(entity_id)})
            return result > 0
        except Exception:
            return False
    
    def save(self, entity: Dict[str, Any]) -> str:
        result = self.collection.insert_one(entity)
        return result(result.inserted_one)


    def find_by_provider(self, provider_id: str) -> List[Dict[str, Any]]:
        try:
            provider_oid = ObjectId(provider_id)
            return list(self.collection.find({"provider_id":provider_oid}))
        except Exception:
            return []
        
    def find_by_business(self, business_id:str) ->List[Dict[str,Any]]:
        try:
            business_oid = ObjectId(business_id)
            return list(self.collection.find({"business_id": business_oid}))
        except Exception:
            return []

    def find_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        return self.collection.find({"name":name})


class MongoDBAvailabilityRepository(AvailabilityRepository):
    def __init__(self, collection):
        self.collection = collection

    def find_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        try:
            return self.collection.find_one({"_id" : ObjectId(entity_id)})
        except Exception:
            return None
        
    def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return self.collection.find_one(query)
        
    def find_all(self, query: Optional[Dict[str, Any]]= None) -> List[Dict[str, Any]]:
        if query:
            return list(self.collection.find(query))
        return list(self.collection.find())
    
    def save(self, entity: Dict[str, Any]) -> str:
        result = self.collection.insert_one(entity)
        return result(result.inserted_one)    
    
    def update(self, entity_id: str, data: Dict[str, Any]) -> bool:
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(entity_id)},
                {"$set": data}
            )
            return result.modified_count >0
        except Exception:
            return False            
        
    def delete(self, entity_id: str) ->bool:
        try:
            result = self.collection.delete_one({"_id": ObjectId(entity_id)})
            return result.modifies_count >  0
        except Exception:
            return False
        
    def find_by_provider(self, provider_id: str, date_range = Optional[tuple[datetime, datetime]]) -> List[Dict[str, Any]]:
        try:
            provider_oid = ObjectId(provider_id)
            query: dict[str, Any] = {"provider_id": provider_oid}

            if date_range:
                start_date, end_date =  date_range
                query["start_date"] = {"$gte":start_date, "$lte":end_date}
            return list(self.collection.find(query).sort("start_time", 1))        
        except Exception:
            return []
        
    def find_active_by_business(self, business_id:str):
        try:
            busines_oid = ObjectId(business_id)
            return list(self.collection.find({"business_id": busines_oid}))        
        except Exception:
            return []
        
    def find_overlapping_availability(self,
                                     availability_id: str,
                                     provider_id: str, 
                                     business_id: str, 
                                     day: daysOfTheWeek, 
                                     start_time: datetime, 
                                     end_time: datetime
                                     ) -> Optional[Dict[str, Any]]:
        try:
            availability_oid = ObjectId(availability_id)
            provider_oid = ObjectId(provider_id)
            business_oid = ObjectId(business_id)
            
            query = {
            "_id" :{"$ne" : availability_oid},
            "provider_id" : provider_oid,
            "business_id" : business_oid,
            "day" : day,
            "$or":[
                {
                    "start_time" : {"$lt": end_time},
                    "end_time" : {"$gt" : start_time}
                }
            ]
            }
            return self.collection.find_one(query)
        except Exception:
            return None
        
        
    
    
            
