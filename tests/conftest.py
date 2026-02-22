"""
Фикстуры для тестирования туристического API.
"""
import pytest
from app import app, db
from models import User, Destination, Tour

@pytest.fixture(scope='function')
def test_app():
    """Создает тестовое приложение Flask."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(test_app):
    """Создает тестовый клиент Flask."""
    return test_app.test_client()

@pytest.fixture(scope='function')
def sample_data(test_app):
    """Создает тестовые данные в БД."""
    with test_app.app_context():
        # Очистка перед созданием
        db.session.query(User).delete()
        db.session.query(Destination).delete()
        db.session.query(Tour).delete()
        
        # Создание тестовых данных
        user = User(name="Тестовый Пользователь", email="test@mail.com", phone="+79990000000")
        destination = Destination(
            name="Тестовый Париж", 
            country="Франция", 
            description="Тестовое описание",
            price=1000.0,
            duration_days=5
        )
        tour = Tour(
            destination_id=1,
            start_date="2024-12-01",
            end_date="2024-12-05",
            available_slots=10,
            is_active=True
        )
        
        db.session.add_all([user, destination, tour])
        db.session.commit()
        
        return {
            'user': user,
            'destination': destination,
            'tour': tour
        }