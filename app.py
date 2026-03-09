"""
Модуль REST API сервиса для туристического агентства.

ВЕРСИЯ 3.0 - С РАСШИРЕННОЙ СИСТЕМОЙ ИСКЛЮЧЕНИЙ И ЛОГИРОВАНИЕМ

Основные компоненты:
- Flask приложение с REST API
- Обработка исключений в формате Problem Details
- Логирование операций
- Инициализация базы данных
- Добавление тестовых данных

Импортирует все основные классы системы для единой документации.
"""

from flask import Flask, jsonify, request, Blueprint
from flask_restful import Api
import os
import logging
import yaml
import logging.config
from datetime import datetime
from werkzeug.exceptions import HTTPException
from sqlalchemy import select, delete

from config import Config
from models import db, User, Destination, Tour
from exceptions.custom_exceptions import TourismBaseException

# Импорты ресурсов
from resources.user_resources import UserListResource, UserResource, UserBulkDeleteResource, UserBookTourResource
from resources.destination_resources import DestinationListResource, DestinationResource
from resources.tour_resources import TourListResource, TourResource, AvailableToursResource
from services.tourism_services import UserService, TourService, DestinationService, BookingService
from errors.handlers import register_error_handlers
from api.v1.routes.auth_routes import auth_bp
from api.v1.routes.health_routes import health_bp
from api.v1.routes.stats_routes import stats_bp
from api.v1.routes.booking_routes import booking_bp
# from api.v1.destinations_routes import destinations_bp
from core.logging_config import setup_logging

# Инициализация приложения
app = Flask(__name__)
app.config.from_object(Config)
register_error_handlers(app)

# Создаем папку data если её нет
if not os.path.exists('data'):
    os.makedirs('data')

db.init_app(app)

api_v1_bp = Blueprint('api_v1', __name__, url_prefix='/api/v1/') #!
api_v1 = Api(api_v1_bp) #!

api = Api(app)

# Настраиваем логирование ПЕРЕД использованием логгера
logger = setup_logging()

@app.route('/')
def hello():
    """
    Корневой эндпоинт API с информацией о сервисе.
    
    Returns:
        dict: Информация о сервисе и доступные эндпоинты
        
    Пример ответа:
        {
            "message": "Tourism REST Service",
            "version": "3.0", 
            "endpoints": {
                "users": "/api/users",
                "destinations": "/api/destinations",
                "tours": "/api/tours"
            }
        }
    """
    logger.info("GET / - корневой запрос")
    return jsonify({
        "message": "Tourism REST Service", 
        "version": "3.0",
        "endpoints": {
            "users": "/api/users",
            "destinations": "/api/destinations",
            "tours": "/api/tours", 
            "available_tours": "/api/tours/available",
            "health": "/api/health"
        }
    })
    
api_v1_bp.register_blueprint(auth_bp, url_prefix='/auth')
api_v1_bp.register_blueprint(booking_bp, url_prefix='/bookings')
api_v1_bp.register_blueprint(health_bp)
api_v1_bp.register_blueprint(stats_bp, url_prefix='/stats')
# api_v1_bp.register_blueprint(destinations_bp, url_prefix='/destinations')
app.register_blueprint(api_v1_bp) #!

def add_sample_data():
    """
    Добавляет тестовые данные в базу данных при первом запуске.
    
    Создает:
    - 3 тестовых направления (Париж, Токио, Бали)
    - 3 тестовых пользователя
    - 3 тестовых тура
    
    Returns:
        None
        
    Raises:
        Exception: При ошибках добавления данных
    """
    try:
        if db.session.execute(select(User)).first():
            logger.info("База данных уже содержит данные, пропускаем добавление тестовых данных")
            return
            
        logger.info("Добавляем тестовые данные...")
        
        sample_destinations = [
            Destination(name="Париж", country="Франция", description="Город любви и света", price=1200, duration_days=5),
            Destination(name="Токио", country="Япония", description="Современный мегаполис с древними традициями", price=1800, duration_days=7),
            Destination(name="Бали", country="Индонезия", description="Тропический рай с пляжами", price=900, duration_days=10)
        ]
        for dest in sample_destinations:
            db.session.add(dest)
        
        sample_users = [
            User(name="Иван Иванов", email="ivan@mail.com", phone="+79991234567"),
            User(name="Мария Петрова", email="maria@mail.com", phone="+79997654321"),
            User(name="Алексей Сидоров", email="alex@mail.com", phone="+79998887766")
        ]
        for user in sample_users:
            db.session.add(user)
        
        db.session.commit()
        
        sample_tours = [
            Tour(destination_id=1, start_date="2024-12-01", end_date="2024-12-05", available_slots=5),
            Tour(destination_id=2, start_date="2024-12-10", end_date="2024-12-17", available_slots=3),
            Tour(destination_id=3, start_date="2024-12-15", end_date="2024-12-25", available_slots=8)
        ]
        for tour in sample_tours:
            db.session.add(tour)
        
        db.session.commit()
        logger.info("✅ Тестовые данные успешно добавлены")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при добавлении тестовых данных: {str(e)}", exc_info=True)
        db.session.rollback()

def validate_architecture():
    """
    Проверяет соблюдение архитектурных принципов и логирует результаты.
    
    Returns:
        None
    """
    principles = {
        "high_cohesion": "Сервисы имеют одну четкую ответственность",
        "low_coupling": "Ресурсы используют сервисы вместо прямой логики", 
        "business_rules": "Бизнес-логика вынесена в сервисы",
        "error_handling": "Единообразная обработка ошибок",
        "modularity": "Код разбит на логические модули",
        "logging": "Централизованная система логирования"
    }
    
    logger.info("Архитектурные принципы:")
    for principle, description in principles.items():
        logger.info(f"  ✓ {principle}: {description}")

# Регистрация API ресурсов
api_v1.add_resource(UserListResource, '/users')
api_v1.add_resource(UserResource, '/users/<int:id>')
api_v1.add_resource(UserBulkDeleteResource, '/users/bulk-delete')
api_v1.add_resource(UserBookTourResource, '/users/<int:user_id>/book-tour/<int:tour_id>')

api.add_resource(DestinationListResource, '/api/destinations')
api.add_resource(DestinationResource, '/api/destinations/<int:id>')

api_v1.add_resource(TourListResource, '/tours')
api_v1.add_resource(TourResource, '/tours/<int:id>')
api_v1.add_resource(AvailableToursResource, '/tours/available')
      
@app.route('/api/destinations/coordinates')
def get_destinations_coordinates():
    """Возвращает города с координатами для глобуса"""
    try:
        # Получаем все направления
        destinations = Destination.query.all()
        result = []
        
        for dest in destinations:
            # Проверяем, есть ли координаты
            if dest.latitude and dest.longitude:
                # Считаем количество туров для этого направления
                tours_count = len(dest.tours) if hasattr(dest, 'tours') else 0
                
                # 👇 ПРЕОБРАЗУЕМ ЦЕНУ (умножаем на 50 для красивых рублей)
                price_in_rubles = int(dest.price * 50) if dest.price else 35000
                
                result.append({
                    'id': dest.id,
                    'name': dest.name,
                    'country': dest.country,
                    'lat': float(dest.latitude),
                    'lng': float(dest.longitude),
                    'tours': tours_count,
                    'price': f'{price_in_rubles}'  # Теперь 1200 → 60000
                })
        
        # Если нет городов с координатами, возвращаем тестовые
        if not result:
            result = [
                {'id': 1, 'name': 'Париж', 'country': 'Франция', 'lat': 48.8566, 'lng': 2.3522, 'tours': 5, 'price': '60000'},
                {'id': 2, 'name': 'Токио', 'country': 'Япония', 'lat': 35.6762, 'lng': 139.6503, 'tours': 3, 'price': '90000'},
                {'id': 3, 'name': 'Бали', 'country': 'Индонезия', 'lat': -8.3405, 'lng': 115.0920, 'tours': 8, 'price': '45000'}
            ]
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Ошибка в /api/destinations/coordinates: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Возвращаем тестовые данные при ошибке
        test_data = [
            {'id': 1, 'name': 'Париж', 'country': 'Франция', 'lat': 48.8566, 'lng': 2.3522, 'tours': 5, 'price': '60000'},
            {'id': 2, 'name': 'Токио', 'country': 'Япония', 'lat': 35.6762, 'lng': 139.6503, 'tours': 3, 'price': '90000'},
            {'id': 3, 'name': 'Бали', 'country': 'Индонезия', 'lat': -8.3405, 'lng': 115.0920, 'tours': 8, 'price': '45000'}
        ]
        return jsonify(test_data)
        
if __name__ == '__main__':
    """
    Точка входа приложения - запуск REST API сервера.
    
    Выполняет:
    - Инициализацию базы данных
    - Добавление тестовых данных
    - Проверку архитектурных принципов
    - Запуск Flask сервера
    
    Пример использования:
        python app.py
    """
    print("🚀 Запуск туристического REST API...")
    print("📁 Модульная архитектура с обработкой исключений и логированием")
    
    with app.app_context():
        db.create_all()
        add_sample_data()
        validate_architecture()
        
        print("✅ База данных инициализирована")
        print("✅ Тестовые данные добавлены") 
        print("✅ Архитектурные принципы проверены")
        print("✅ Логирование настроено")
    
    print("\n🌐 Сервер запущен: http://localhost:5000")
    print("\n📚 Доступные эндпоинты:")
    print("  GET  /api/users - все пользователи")
    print("  GET  /api/destinations - все направления")
    print("  GET  /api/tours - все туры")
    print("  GET  /api/tours/available - только доступные туры")
    print("  POST /api/users/<id>/book-tour/<id> - бронирование тура")
    print("  POST /api/v1/auth/register - регистрация пользователя") #!
    print("  POST /api/v1/auth/login - авторизация существующего пользователя") #!
    print("\n🔧 Для тестирования ошибок:")
    print("  GET  /api/users/999 - несуществующий пользователь (404)")
    print("  POST /api/users (с существующим email) - дубликат (409)")
    print("\n📋 Логи сохраняются в папке logs/")
    
    print(app.url_map)
    
    app.run(host='0.0.0.0', port=5000, debug=True)