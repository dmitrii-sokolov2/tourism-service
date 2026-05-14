from core.database import Base
from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, DateTime, Float,
    Boolean, Text, ForeignKey, Table
)
from sqlalchemy.orm import relationship

user_tour = Table(
    'user_tour',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('tour_id', Integer, ForeignKey('tours.id'), primary_key=True),
    Column('booking_date', DateTime, default=datetime.utcnow),
    Column('status', String(20), default='confirmed')
)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    password_hash = Column(String(255))
    
    booked_tours = relationship(
        'Tour',
                secondary=user_tour,
                back_populates='users'
    )
    refresh_tokens = relationship('RefreshToken', back_populates='user')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'booked_tours_count': len(self.booked_tours)
        }

class Destination(Base):
    __tablename__ = 'destinations'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    country = Column(String(50), nullable=False)
    description = Column(Text)
    price = Column(Float)
    duration_days = Column(Integer)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    rating = Column(Float, default=4.5)
    tour_type = Column(String(50), default='Экскурсионный')
    hotel_stars = Column(Integer, default=3)
    transfer = Column(Boolean, default=False)
    # created_at = Column(DateTime, default=datetime.utcnow)

    tours = relationship(
        'Tour',
        back_populates='destination',
        cascade='all, delete-orphan'
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'country': self.country,
            'description': self.description,
            'price': self.price,
            'duration_days': self.duration_days,
            # 'created_at': self.created_at.isoformat() if self.created_at else None,
            'tours_count': len(self.tours)
        }

class Tour(Base):
    __tablename__ = 'tours'
    
    id = Column(Integer, primary_key=True)
    destination_id = Column(Integer, ForeignKey('destinations.id'), nullable=False)
    start_date = Column(String(50), nullable=False)
    end_date = Column(String(50), nullable=False)
    available_slots = Column(Integer, default=10)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    destination = relationship(
        'Destination',
        back_populates='tours'
    )

    users = relationship(
        'User',
        secondary=user_tour,
        back_populates='booked_tours'
    )

    def to_dict(self):
        return {
            'id': self.id,
            # 'destination_id': self.destination_id,
            # 'destination_name': self.destination.name if self.destination else None,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'available_slots': self.available_slots,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'users_count': len(self.users),
            # 'price': self.destination.price if self.destination else None
        }

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="refresh_tokens")

    token_hash = Column(String(255), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class PromoCode(Base):
    __tablename__ = "promo_codes"

    id = Column(Integer, primary_key=True)

    code = Column(String(50), unique=True, nullable=False)

    discount_percent = Column(Integer, nullable=True)
    discount_amount = Column(Float, nullable=True)

    is_active = Column(Boolean, default=True)

    usage_limit = Column(Integer, nullable=True)
    used_count = Column(Integer, nullable=True)

    min_price = Column(Float, nullable=True)

    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)