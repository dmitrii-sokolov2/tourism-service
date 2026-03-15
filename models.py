from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Инициализируем db здесь
db = SQLAlchemy()

# Таблица для отношения многие-ко-многим (User-Tour)
user_tour = db.Table('user_tour',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('tour_id', db.Integer, db.ForeignKey('tours.id'), primary_key=True),
    db.Column('booking_date', db.DateTime, default=datetime.utcnow),
    db.Column('status', db.String(20), default='confirmed')
)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Отношение многие-ко-многим с Tour
    booked_tours = db.relationship('Tour', secondary=user_tour, backref=db.backref('users', lazy=True))
    refresh_tokens = db.relationship('RefreshToken', back_populates='user')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'booked_tours_count': len(self.booked_tours)
        }

class Destination(db.Model):  
    __tablename__ = 'destinations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    duration_days = db.Column(db.Integer)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    
    # Связи
    tours = db.relationship('Tour', backref='destination', lazy=True)
    
    # Отношение один-ко-многим с Tour
    tours = db.relationship('Tour', backref='destination', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'country': self.country,
            'description': self.description,
            'price': self.price,
            'duration_days': self.duration_days,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'tours_count': len(self.tours)
        }

class Tour(db.Model):
    __tablename__ = 'tours'
    
    id = db.Column(db.Integer, primary_key=True)
    destination_id = db.Column(db.Integer, db.ForeignKey('destinations.id'), nullable=False)
    start_date = db.Column(db.String(50), nullable=False)
    end_date = db.Column(db.String(50), nullable=False)
    available_slots = db.Column(db.Integer, default=10)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'destination_id': self.destination_id,
            'destination_name': self.destination.name if self.destination else None,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'available_slots': self.available_slots,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'users_count': len(self.users)
        }

class RefreshToken(db.Model):
    __tablename__ = "refresh_tokens"
    
    id = db.Column(db.Integer, primary_key=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", back_populates="refresh_tokens")

    token_hash = db.Column(db.String(255), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    