import bcrypt, jwt, secrets, hashlib
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from pydantic import BaseModel
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session

from config import Config
from models.models import RefreshToken, User
from core.database import get_db

SECRET_KEY = Config.SECRET_KEY

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)

    return hashed.decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_access_token(user_id: int, email: str) -> str:
    payload = {
        "id": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(minutes=10)
    }

    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def create_refresh_token(user_id: int, db: Session = Depends(get_db)) -> str:
    token = secrets.token_urlsafe(32)
    token_hash = hash_token(token)

    refresh = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )

    db.add(refresh)
    db.commit()

    return token

def register_user(data: BaseModel, db: Session = Depends(get_db)) -> dict:
    password_hash = hash_password(data["password"])

    user = User(
        **data.model_dump(exclude={"password"}),
        password_hash=password_hash
    )

    try:
        db.add(user)
        db.commit()
    except IntegrityError:
        db.rollback()

        raise HTTPException(status_code=400, detail="user already exists")

    return {
        "id": user.id,
        "email": user.email
    }

def login_user(email, password, db: Session = Depends(get_db)) -> dict:
    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="User does not exist")

    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="invalid password")

    access_token = create_access_token(user.id, user.email)
    refresh_token = create_refresh_token(user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }