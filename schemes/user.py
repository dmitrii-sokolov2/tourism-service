from pydantic import BaseModel, EmailStr, field_validator
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