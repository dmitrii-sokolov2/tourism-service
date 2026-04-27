from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional

class UserRegisterSchema(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None 
    password: str
    
    @field_validator("email")
    @classmethod
    def normalize_email(cls, v):
        return v.lower()

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str

class UserCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=20)
    password: str = Field(..., min_length=6, max_length=255)

class UserUpdateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=20)
    password: str = Field(..., min_length=6, max_length=255)

class UserBulkDeleteSchema(BaseModel):
    user_ids: list[int] = Field(..., min_length=1)