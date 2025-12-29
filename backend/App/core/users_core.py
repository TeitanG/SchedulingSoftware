

def validar_username_email(email: str,
                           username:str,
                           existing_user:list):
    
       
    for user in existing_user:
        if user["username"] == username:
            raise ValueError("El username ya existe") 
        if user["email"] == email:
            raise ValueError("El email ya existe")
        

def validar_username(username : str,
                     existing_usernames : list):
    
    for user in existing_usernames:
        if user["username"] == username:
            raise ValueError("El username ya existe")
        
def validar_email(email : str,
                  existing_emails : list):
    for user in existing_emails:
        if user["email"] == email:
            raise ValueError("El email ya existe")
        

    
