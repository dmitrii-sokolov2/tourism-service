"""
Тесты для валидаторов JSON схем.
"""
import pytest
from validators.user_validator import UserValidator
from validators.destination_validator import DestinationValidator
from validators.tour_validator import TourValidator
from jsonschema.exceptions import ValidationError

# --- Тесты UserValidator ---
def test_user_validator_add_valid():
    """Тест валидации корректных данных пользователя для добавления."""
    validator = UserValidator()
    valid_data = {
        "name": "Иван Иванов",
        "email": "ivan@example.com",
        "phone": "+79991234567"
    }
    
    # Заменяем assert на try/except
    try:
        validator.validate_user(valid_data, 'add')
        assert True  # Если не вызвало исключение - тест пройден
    except ValidationError:
        assert False  # Если вызвало исключение - тест не пройден

def test_user_validator_add_invalid():
    """Тест валидации некорректных данных пользователя."""
    validator = UserValidator()
    invalid_data = {
        "name": "",  # Пустое имя
        "email": "invalid-email",  # Некорректный email
        "phone": "123"  # Слишком короткий телефон
    }
    
    with pytest.raises(ValidationError):
        validator.validate_user(invalid_data, 'add')

def test_user_validator_update_valid():
    """Тест валидации данных для обновления (не все поля обязательны)."""
    validator = UserValidator()
    valid_data = {
        "name": "Новое Имя"  # Только имя, остальные можно не указывать
    }
    
    # Заменяем assert на try/except
    try:
        validator.validate_user(valid_data, 'update')
        assert True
    except ValidationError:
        assert False

# --- Тесты DestinationValidator ---
def test_destination_validator_add_valid():
    """Тест валидации корректных данных направления."""
    validator = DestinationValidator()
    valid_data = {
        "name": "Париж",
        "country": "Франция",
        "description": "Город любви",
        "price": 1200.0,
        "duration_days": 5
    }
    
    # Заменяем assert на try/except
    try:
        validator.validate_destination(valid_data, 'add')
        assert True
    except ValidationError:
        assert False

def test_destination_validator_add_missing_required():
    """Тест валидации без обязательных полей."""
    validator = DestinationValidator()
    invalid_data = {
        "name": "Париж",
        # Нет country - должно вызвать ошибку
        "price": 1200.0
    }
    
    with pytest.raises(ValidationError):
        validator.validate_destination(invalid_data, 'add')

def test_destination_validator_invalid_price():
    """Тест валидации с отрицательной ценой через JSON схему."""
    validator = DestinationValidator()
    invalid_data = {
        "name": "Париж",
        "country": "Франция",
        "price": -100.0,  # Отрицательная цена
        "duration_days": 5
    }
    
    with pytest.raises(ValidationError):
        validator.validate_destination(invalid_data, 'add')

# --- Тесты TourValidator ---
def test_tour_validator_add_valid():
    """Тест валидации корректных данных тура."""
    validator = TourValidator()
    valid_data = {
        "destination_id": 1,
        "start_date": "2024-12-01",
        "end_date": "2024-12-05",
        "available_slots": 10,
        "is_active": True
    }
    
    # Заменяем assert на try/except
    try:
        validator.validate_tour(valid_data, 'add')
        assert True
    except ValidationError:
        assert False

def test_tour_validator_invalid_date_format():
    """Тест валидации с некорректным форматом даты."""
    validator = TourValidator()
    invalid_data = {
        "destination_id": 1,
        "start_date": "01-12-2024",  # Неправильный формат
        "end_date": "05-12-2024"
    }
    
    with pytest.raises(ValidationError):
        validator.validate_tour(invalid_data, 'add')

def test_tour_validator_negative_slots():
    """Тест валидации с отрицательным количеством мест."""
    validator = TourValidator()
    invalid_data = {
        "destination_id": 1,
        "start_date": "2024-12-01",
        "end_date": "2024-12-05",
        "available_slots": -5  # Отрицательное количество
    }
    
    with pytest.raises(ValidationError):
        validator.validate_tour(invalid_data, 'add')