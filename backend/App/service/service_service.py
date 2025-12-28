from App.db.client import db_client
from App.db.schemas import serviceSchema

def create_services(
        name : str,
        description : str,
        price : int,
        provider_id : str,
        business_id : str
        ):
    



    
    services_db = {
        "name" : name,
        "description" : description,
        "price" : price,
        "provider" : provider_id,
        "business_id" : business_id
    }

    insert_id = db_client.services.insert_one(services_db).inserted_id
    new_service = db_client.services.find_one({"_id":insert_id})

    

    




    return serviceSchema(new_service)







    




    




