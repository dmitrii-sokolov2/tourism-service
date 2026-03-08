from pydantic import BaseModel, EmailStr, field_validator

class UserRegisterSchema(BaseModel):
    name: str
    email: EmailStr
    phone: str
    password: str
    
    @field_validator("email")
    @classmethod
    def normalize_email(cls, v):
        return v.lower()