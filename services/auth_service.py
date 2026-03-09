import bcrypt, jwt, secrets, hashlib
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from flask import jsonify


from config import Config
from models import db, User, RefreshToken
from schemes.user import UserRegisterSchema

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
    
def create_refresh_token(user_id: int):
    token = secrets.token_urlsafe(32)
    token_hash = hash_token(token)
    
    refresh = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    
    db.session.add(refresh)
    db.session.commit()
    
    return token
    
def register_user(data: UserRegisterSchema):
    password_hash = hash_password(data.password)

    new_user = User(
        name=data.name,
        email=data.email,
        phone=data.phone,
        password_hash=password_hash
    )
    
    try: 
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Exception("User with this email already exists")
    except Exception as e:
        raise Exception(e)

    return {
        "id": new_user.id,
        "email": new_user.email
    }

def login_user(email, password):
    user = User.query.filter_by(email=email).first()

    if not user:
        raise Exception("User not found")

    if not verify_password(password, user.password_hash):
        raise Exception("Invalid password")

    access_token = create_access_token(user.id, user.email)
    refresh_token = create_refresh_token(user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }