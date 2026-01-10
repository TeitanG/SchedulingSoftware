from App.core import validar_transicion_estado

def validar_username_email(email: str,
                           username:str,
                           existing_user:list):           
    for item in existing_user:
        stored_username = item.get("username")

        if stored_username is None:
            continue

        if stored_username == username:
            raise ValueError("El nombre de usuario ya existe")
        
    for item in existing_user:
        stored_email = item.get("email")

        if stored_email is None:
            continue

        if stored_email == email:
            raise ValueError("El correo electronico ya esta registrado")        

        

def validar_username(username : str,
                     existing_usernames : list):
    
    for item in existing_usernames:
        stored_username = item.get("username")

        if stored_username is None:
            continue

        if stored_username == username:
            raise ValueError("El nombre de usuario ya existe")
 
def validar_email(email : str,
                  existing_emails : list):
    
    for item in existing_emails:
        stored_email = item.get("email")

        if stored_email is None:
            continue

        if stored_email == email:
            raise ValueError("El correo electronico ya esta registrado")
        

def user_types():
    return {
        "admin",
        "provider",
        "user"
    }


def validar_crear_cita(actor_rol:str)->bool:    

    if not user_types:
        raise PermissionError("No se puede crear la cita")
    
    return True







    
