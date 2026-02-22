"""
Модуль моделей базы данных для туристического агентства.

Содержит SQLAlchemy модели:
- User: Пользователи системы
- Destination: Туристические направления  
- Tour: Конкретные туры с датами
- user_tour: Таблица связи многие-ко-многим (User-Tour)

Отношения:
- User <-> Tour: Many-to-Many (через user_tour)
- Destination -> Tour: One-to-Many

Автор: [Соколов Дмитрий]
Версия: 3.0
"""

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
    """
    Модель пользователя системы.
    
    Атрибуты:
        id (int): Первичный ключ
        name (str): Имя пользователя (обязательно)
        email (str): Email (уникальный, обязательно) 
        phone (str): Телефонный номер
        created_at (datetime): Дата создания
        booked_tours (list): Список забронированных туров
        
    Методы:
        to_dict(): Преобразует объект в словарь
        
    Пример:
        user = User(name="Иван", email="ivan@mail.com")
    """
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Отношение многие-ко-многим с Tour
    booked_tours = db.relationship('Tour', secondary=user_tour, backref=db.backref('users', lazy=True))
    
    def to_dict(self):
        """
        Преобразует объект пользователя в словарь.
        
        Returns:
            dict: Словарь с данными пользователя
            
        Пример:
            >>> user.to_dict()
            {
                'id': 1,
                'name': 'Иван Иванов',
                'email': 'ivan@mail.com',
                'phone': '+79991234567',
                'created_at': '2024-01-15T10:30:00',
                'booked_tours_count': 2
            }
        """
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'booked_tours_count': len(self.booked_tours)
        }

class Destination(db.Model):
    """
    Модель туристического направления.
    
    Атрибуты:
        id (int): Первичный ключ
        name (str): Название направления (обязательно)
        country (str): Страна (обязательно)
        description (str): Описание направления
        price (float): Стоимость тура
        duration_days (int): Продолжительность в днях
        created_at (datetime): Дата создания
        tours (list): Список связанных туров
        
    Методы:
        to_dict(): Преобразует объект в словарь
    """
    
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
        """
        Преобразует объект направления в словарь.
        
        Returns:
            dict: Словарь с данными направления
            
        Пример:
            >>> destination.to_dict()
            {
                'id': 1,
                'name': 'Париж',
                'country': 'Франция', 
                'description': 'Город любви',
                'price': 1200.0,
                'duration_days': 5,
                'created_at': '2024-01-15T10:30:00',
                'tours_count': 3
            }
        """
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
    """
    Модель конкретного тура с датами и доступными местами.
    
    Атрибуты:
        id (int): Первичный ключ
        destination_id (int): ID направления (внешний ключ)
        start_date (str): Дата начала тура (обязательно)
        end_date (str): Дата окончания тура (обязательно)
        available_slots (int): Доступные места
        is_active (bool): Активен ли тур
        created_at (datetime): Дата создания
        
    Методы:
        to_dict(): Преобразует объект в словарь
    """
    
    __tablename__ = 'tours'
    
    id = db.Column(db.Integer, primary_key=True)
    destination_id = db.Column(db.Integer, db.ForeignKey('destinations.id'), nullable=False)
    start_date = db.Column(db.String(50), nullable=False)
    end_date = db.Column(db.String(50), nullable=False)
    available_slots = db.Column(db.Integer, default=10)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """
        Преобразует объект тура в словарь.
        
        Returns:
            dict: Словарь с данными тура
            
        Пример:
            >>> tour.to_dict()
            {
                'id': 1,
                'destination_id': 1,
                'destination_name': 'Париж',
                'start_date': '2024-12-01',
                'end_date': '2024-12-05', 
                'available_slots': 5,
                'is_active': True,
                'created_at': '2024-01-15T10:30:00',
                'users_count': 2
            }
        """
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