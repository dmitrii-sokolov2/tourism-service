"""
Тесты для сервисов бизнес-логики.
"""
import pytest
from services.tourism_services import (
    UserService, DestinationService, TourService, BookingService
)
from exceptions.custom_exceptions import (
    UserNotFoundException, UserEmailDuplicateException, UserValidationException,
    DestinationNotFoundException, DestinationNameDuplicateException, DestinationValidationException,
    TourNotFoundException, TourValidationException, TourDateException, NoAvailableSlotsException  # ← ДОБАВЬТЕ TourDateException
)

# --- Тесты UserService ---
def test_get_user_by_id_success(sample_data):
    """Тест успешного поиска пользователя по ID."""
    user = UserService.get_user_by_id(1)
    assert user is not None
    assert user.id == 1
    assert user.name == "Тестовый Пользователь"

def test_get_user_by_id_not_found(sample_data):
    """Тест поиска несуществующего пользователя."""
    with pytest.raises(UserNotFoundException) as exc_info:
        UserService.get_user_by_id(999)
    assert exc_info.value.status_code == 404

@pytest.mark.usefixtures("test_app")
def test_validate_user_data_valid(test_app):
    """Тест валидации корректных данных пользователя."""
    with test_app.app_context():
        data = {
            "name": "Новый Пользователь",
            "email": "newuser@mail.com"
        }
        # Должно пройти без исключений
        UserService.validate_user_data(data)

def test_validate_user_data_duplicate_email(sample_data):
    """Тест валидации с дублирующимся email."""
    data = {
        "name": "Другой Пользователь",
        "email": "test@mail.com"  # Уже существует
    }
    with pytest.raises(UserEmailDuplicateException) as exc_info:
        UserService.validate_user_data(data)
    assert exc_info.value.status_code == 409

@pytest.mark.usefixtures("test_app")
def test_validate_user_data_invalid_email(test_app):
    """Тест валидации с некорректным email."""
    with test_app.app_context():
        data = {
            "name": "Пользователь",
            "email": "invalid-email"  # Некорректный формат
        }
        with pytest.raises(UserValidationException) as exc_info:
            UserService.validate_user_data(data)
        assert exc_info.value.status_code == 422

# --- Тесты DestinationService ---
def test_get_destination_by_id_success(sample_data):
    """Тест успешного поиска направления по ID."""
    destination = DestinationService.get_destination_by_id(1)
    assert destination is not None
    assert destination.id == 1
    assert destination.name == "Тестовый Париж"

@pytest.mark.usefixtures("test_app")
def test_validate_destination_data_valid(test_app):
    """Тест валидации корректных данных направления."""
    with test_app.app_context():
        data = {
            "name": "Новое Направление",
            "country": "Новая Страна",
            "price": 1500.0,
            "duration_days": 7
        }
        # Должно пройти без исключений
        DestinationService.validate_destination_data(data)

@pytest.mark.usefixtures("test_app")
def test_validate_destination_data_negative_price(test_app):
    """Тест валидации с отрицательной ценой."""
    with test_app.app_context():
        data = {
            "name": "Направление",
            "country": "Страна",
            "price": -100.0,  # Отрицательная цена
            "duration_days": 5
        }
        with pytest.raises(DestinationValidationException) as exc_info:
            DestinationService.validate_destination_data(data)
        assert exc_info.value.status_code == 422

# --- Тесты TourService ---
def test_get_tour_by_id_success(sample_data):
    """Тест успешного поиска тура по ID."""
    tour = TourService.get_tour_by_id(1)
    assert tour is not None
    assert tour.id == 1
    assert tour.available_slots == 10

def test_validate_tour_creation_valid(sample_data):
    """Тест валидации корректных данных тура."""
    data = {
        "destination_id": 1,
        "start_date": "2024-12-10",
        "end_date": "2024-12-15"
    }
    # Должно пройти без исключений
    TourService.validate_tour_creation(data)

@pytest.mark.usefixtures("test_app")
def test_validate_tour_creation_invalid_dates(test_app, sample_data):  
    """Тест валидации с некорректными датами."""
    with test_app.app_context():
        data = {
            "destination_id": 1,
            "start_date": "2024-12-15",  
            "end_date": "2024-12-10"
        }
        with pytest.raises(TourDateException) as exc_info:  # ← Теперь должно работать!
            TourService.validate_tour_creation(data)

def test_decrease_available_slots_success(sample_data):
    """Тест уменьшения доступных мест."""
    tour = TourService.get_tour_by_id(1)
    initial_slots = tour.available_slots
    
    TourService.decrease_available_slots(tour, 2)
    assert tour.available_slots == initial_slots - 2

def test_decrease_available_slots_insufficient(sample_data):
    """Тест уменьшения мест при недостаточном количестве."""
    tour = TourService.get_tour_by_id(1)
    tour.available_slots = 1  # Оставляем только 1 место
    
    with pytest.raises(NoAvailableSlotsException) as exc_info:
        TourService.decrease_available_slots(tour, 5)
    assert exc_info.value.status_code == 403