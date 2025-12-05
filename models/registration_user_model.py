from dataclasses import Field
from typing import Optional
from pydantic import BaseModel, EmailStr

from constants.roles import Roles


class RegistrationUser(BaseModel):
    email: EmailStr
    fullName: str
    password: str = Field(..., min_length=8)
    passwordRepeat: str
    roles: list[Roles]
    banned: Optional[bool] = None
    verified: Optional[bool] = None


