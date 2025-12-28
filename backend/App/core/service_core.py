

def check_name(name : str, existing_name : list):
    
    for name_ in existing_name:
        if name_["name"] == name:
            raise ValueError("Este servicio ya existe")
        
