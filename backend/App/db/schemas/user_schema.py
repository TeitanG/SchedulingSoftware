from pydantic import BaseModel, EmailStr

from App.db.models.user import UserRole, Status


class UserBase(BaseModel):
    role: UserRole
    username: str
    name: str
    business_id: str
    email: EmailStr
    user_status: Status


def user_to_dict(user) -> dict:
    return {
        "id": str(user["_id"]),
        "role": user["role"].value if hasattr(user["role"], "value") else user["role"],
        "username": user["username"],
        "name": user["name"],
        "business_id": (
            str(user["business_id"]) if user.get("business_id") is not None else None
        ),
        "email": user["email"],
        "user_status": user["user_status"].value
        if hasattr(user["user_status"], "value")
        else user["user_status"],
    }


def users_to_dict(users) -> list:

    result = []

    for user in users:
        result.append(user_to_dict(user))
    return result


class UserPatch(BaseModel):
    role: UserRole | None = None
    username: str | None = None
    name: str | None = None
    business_id: str | None = None
    email: EmailStr | None = None
    user_status: Status | None = None


class UserCreate(UserBase):
    pass


class UserPut(UserBase):
    pass
