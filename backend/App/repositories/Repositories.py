from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import datetime
from App.db.models import StatusAppointments, user_Status, user_Type, BusinessType, daysOfTheWeek


class Repository(ABC):

    @abstractmethod
    def find_by_id(self, entity_id:str)-> Optional[Dict[str, Any]]:
        pass    

    @abstractmethod
    def find_one(self, query: Dict)-> Optional[Dict[str,Any]]:
        pass

    @abstractmethod
    def find_all(self, query: Optional[dict]= None)-> List[Dict[str, Any]]:
        pass   
    
    @abstractmethod
    def save(self, entity:Dict[str, Any])->str:
        pass

    @abstractmethod
    def update(self, entity_id:str, data: Dict[str, Any])->bool:
        pass

    @abstractmethod
    def delete(self, entity_id:str)->bool:
        pass
    

class UserRepository(Repository):

    @abstractmethod
    def find_by_username(self, username:str) -> Optional[Dict[str,Any]]:
        pass

    @abstractmethod
    def find_by_email(self, email:str)-> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def find_by_role(self, role: user_Type)-> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def find_by_status(self, status: user_Status) ->List[Dict[str, Any]]:
        pass

class BusinessRepository(Repository):

    @abstractmethod
    def find_by_name(self, name: str)-> Optional[Dict[str, Any]]:
        pass 

    @abstractmethod
    def find_active(self) ->List[Dict[str,Any]]:
        pass

    @abstractmethod
    def find_by_type(self, type: BusinessType)-> List[Dict[str,Any]]:
        pass
    

class ServiceRepository(Repository):

    @abstractmethod
    def find_by_provider(self, provider_id: str, date_range : Optional[tuple[datetime,datetime]] = None)-> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def find_by_name(self, name:str) -> Optional[Dict[str, Any]]:
        pass


class AppointmentRepository(Repository):

    @abstractmethod
    def find_by_provider(self, provider_id :str, date_range: Optional[tuple]= None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def find_by_client(self, client_id:str, date_range: Optional[tuple] = None) -> List[Dict[str,Any]]:
        pass

    @abstractmethod
    def find_overlapping(self, provider_id:str, start_time:datetime, end_time:datetime) -> List[Dict[str,Any]]:
        pass

    @abstractmethod
    def find_by_status(self, status: StatusAppointments) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def find_pending_and_confirmed(self)-> List[Dict[str, Any]]:
        pass


class AvailabilityRepository(Repository):

    @abstractmethod
    def find_by_provider(self, provider_id: str, date_range :Optional[tuple[datetime,datetime]])-> List[Dict[str, Any]]:
        pass
    

    @abstractmethod
    def find_active_by_business(self, business_id: str)-> List[Dict[str,Any]]:
        pass

    @abstractmethod
    def find_overlapping_availability(
        self,
        availability_id : str,
        provider_id : str,
        business_id : str,
        day : daysOfTheWeek,
        start_time : datetime,
        end_time : datetime,        
    ) -> Optional[Dict[str,Any]]:
        pass

    
