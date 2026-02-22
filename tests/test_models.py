"""
Тесты для моделей базы данных.
"""
import pytest
from datetime import datetime
from models import User, Destination, Tour

def test_user_model():
    """Тест создания модели пользователя."""
    user = User(
        name="Иван Иванов",
        email="ivan@mail.com",
        phone="+79991234567"
    )
    
    assert user.name == "Иван Иванов"
    assert user.email == "ivan@mail.com"
    assert isinstance(user.created_at, datetime) or user.created_at is None
    assert user.booked_tours == []

def test_user_to_dict():
    """Тест метода to_dict() для пользователя."""
    user = User(name="Тест", email="test@mail.com")
    user_dict = user.to_dict()
    
    assert 'id' in user_dict
    assert user_dict['name'] == "Тест"
    assert user_dict['email'] == "test@mail.com"
    assert 'booked_tours_count' in user_dict
    assert user_dict['booked_tours_count'] == 0

def test_destination_model():
    """Тест создания модели направления."""
    destination = Destination(
        name="Париж",
        country="Франция",
        price=1200.0,
        duration_days=5
    )
    
    assert destination.name == "Париж"
    assert destination.country == "Франция"
    assert destination.price == 1200.0
    assert destination.duration_days == 5
    assert destination.tours == []

def test_tour_model():
    """Тест создания модели тура."""
    tour = Tour(
        destination_id=1,
        start_date="2024-12-01",
        end_date="2024-12-05",
        available_slots=5,
        is_active=True  
    )
    
    assert tour.destination_id == 1
    assert tour.start_date == "2024-12-01"
    assert tour.end_date == "2024-12-05"
    assert tour.available_slots == 5
    assert tour.is_active == True

def test_relationships():
    """Тест связей между моделями."""
    # Создаем объекты
    destination = Destination(name="Париж", country="Франция")
    tour = Tour(destination_id=1, start_date="2024-12-01", end_date="2024-12-05")
    user = User(name="Иван", email="ivan@mail.com")
    
    # Проверяем связи
    assert len(destination.tours) == 0
    tour.destination = destination
    assert tour.destination == destination
    
    # Проверяем связь многие-ко-многим
    assert len(user.booked_tours) == 0
    user.booked_tours.append(tour)
    assert len(user.booked_tours) == 1
    assert tour in user.booked_tours