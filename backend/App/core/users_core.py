def user_types():
    return {"admin", "provider", "user"}


def validar_crear_cita(actor_rol: str) -> bool:

    if actor_rol not in user_types():
        raise PermissionError("No se puede crear la cita")

    return True
