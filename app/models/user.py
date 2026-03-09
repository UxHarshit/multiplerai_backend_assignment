from pydantic import BaseModel, EmailStr, Field, field_validator
from enum import Enum

class Role(str, Enum):
    admin = "admin"
    user = "user"

class UserInDB(BaseModel):
    username: str
    email: EmailStr
    hashed_password: str
    role: Role = Role.user

class SignupRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: Role = Role.user         

    @field_validator("password")
    @classmethod
    def validate_password_length_for_bcrypt(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be 72 bytes or fewer.")
        return value

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    username: str
    email: EmailStr
    role: Role

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse