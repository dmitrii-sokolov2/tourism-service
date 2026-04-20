from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
from schemes.user import UserRegisterSchema, UserLoginSchema
from services.auth_service import register_user, login_user

auth_router = APIRouter(prefix='/auth', tags=["auth"])

@auth_router.post('/register', status_code=201)
def register(payload: UserRegisterSchema):
    if not payload:
        raise HTTPException(status_code=400, detail="JSON body required")

    try:
        user = register_user(payload)
    except ValidationError as e:

        raise HTTPException(status_code=409, detail=e.json())

    return {"message": "user has been created",
            "data": user}

@auth_router.post('/login', status_code=200)
def login(payload: UserLoginSchema):
    if not payload:
        raise HTTPException(status_code=400, detail="JSON body required")

    result = login_user(
        payload.email.lower(),
        payload.password
    )

    return result