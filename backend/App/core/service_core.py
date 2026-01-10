

def check_name(value : str, existing_name : list, field: str = "name"):
    
    for item in existing_name:
        if item.get(field)== value:
            raise ValueError(f"el valor {value} ya existe")
        
