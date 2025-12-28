

def validar_username_email(email: str,
                           username:str,
                           existing_user:list):
    
       
    for user in existing_user:
        if user["username"] == username:
            raise ValueError("El username ya existe") 
        if user["email"] == email:
            raise ValueError("El email ya existe")
        





    



    
    
    
