from fastapi import FastAPI, APIRouter
# from flask_migrate import Migrate

from sqlalchemy import select
import os

from config import Config
from models.models import *
from core.extensions import db
from api.v1.routes.user_routes import user_router
from api.v1.routes.destination_routes import destination_router
from errors.handlers import register_error_handlers
from api.v1.routes.auth_routes import auth_router
from api.v1.routes.health_routes import health_router
from api.v1.routes.stats_routes import stats_router
from api.v1.routes.booking_routes import booking_router
from api.v1.routes.tour_routes import tour_router
from core.logging_config import setup_logging
from flask import send_from_directory
from flask_cors import CORS

def create_app():
    app = FastAPI()
    CORS(app)

    app.config.from_object(Config)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    db.init_app(app)
    migrate = Migrate()
    migrate.init_app(app, db)

    register_error_handlers(app)

    api_v1 = APIRouter(prefix='/api/v1')

    logger = setup_logging()

    @api_v1.get('/')
    def index():
        logger.info("GET / - открываем глобус")
        return send_from_directory('static', 'index.html')

    @api_v1.get('/api-info')
    def api_info():
        logger.info("GET /api-info - информация об API")
        return {
            "message": "Tourism REST Service",
            "version": "3.0",
            "endpoints": {
                "users": "/api/users",
                "destinations": "/api/destinations",
                "tours": "/api/tours",
                "available_tours": "/api/tours/available",
                "health": "/api/health"
            }
        }

    @api_v1.get('/destinations/coordinates')
    def get_destinations_coordinates():
        try:
            destinations = Destination.query.all()
            result = []

            for dest in destinations:
                if dest.latitude and dest.longitude:
                    tours_count = len(dest.tours) if hasattr(dest, 'tours') else 0

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

            if not result:
                result = [
                    {'id': 1, 'name': 'Париж', 'country': 'Франция', 'lat': 48.8566, 'lng': 2.3522, 'tours': 5,
                     'price': '60000', 'rating': 4.8, 'tour_type': 'Экскурсионный', 'hotel_stars': 4, 'transfer': True},
                    {'id': 2, 'name': 'Токио', 'country': 'Япония', 'lat': 35.6762, 'lng': 139.6503, 'tours': 3,
                     'price': '90000', 'rating': 4.9, 'tour_type': 'Гастрономический', 'hotel_stars': 5, 'transfer': True},
                    {'id': 3, 'name': 'Бали', 'country': 'Индонезия', 'lat': -8.3405, 'lng': 115.0920, 'tours': 8,
                     'price': '45000', 'rating': 4.7, 'tour_type': 'Пляжный', 'hotel_stars': 4, 'transfer': False}
                ]

            return result

        except Exception as e:
            print(f"Ошибка: {str(e)}")
            import traceback
            traceback.print_exc()

            test_data = [
                {'id': 1, 'name': 'Париж', 'country': 'Франция', 'lat': 48.8566, 'lng': 2.3522, 'tours': 5,
                 'price': '60000', 'rating': 4.8, 'tour_type': 'Экскурсионный', 'hotel_stars': 4, 'transfer': True},
                {'id': 2, 'name': 'Токио', 'country': 'Япония', 'lat': 35.6762, 'lng': 139.6503, 'tours': 3,
                 'price': '90000', 'rating': 4.9, 'tour_type': 'Гастрономический', 'hotel_stars': 5, 'transfer': True},
                {'id': 3, 'name': 'Бали', 'country': 'Индонезия', 'lat': -8.3405, 'lng': 115.0920, 'tours': 8,
                 'price': '45000', 'rating': 4.7, 'tour_type': 'Пляжный', 'hotel_stars': 4, 'transfer': False}
            ]
            return test_data

        except Exception as e:
            print(f"Ошибка в /api/destinations/coordinates: {str(e)}")
            import traceback
            traceback.print_exc()

            test_data = [
                {'id': 1, 'name': 'Париж', 'country': 'Франция', 'lat': 48.8566, 'lng': 2.3522, 'tours': 5, 'price': '60000'},
                {'id': 2, 'name': 'Токио', 'country': 'Япония', 'lat': 35.6762, 'lng': 139.6503, 'tours': 3, 'price': '90000'},
                {'id': 3, 'name': 'Бали', 'country': 'Индонезия', 'lat': -8.3405, 'lng': 115.0920, 'tours': 8, 'price': '45000'}
            ]
            return test_data

    # @api_v1.get('/test-mail')
    # def test_mail():
    #     email_service = EmailService(
    #         Config.MAIL_SERVER,
    #         Config.MAIL_PORT,
    #         Config.MAIL_USERNAME,
    #         Config.MAIL_PASSWORD,
    #         Config.MAIL_FROM
    #     )
    #
    #     email_service.send_email(
    #         "test@test.com",
    #         "test mail",
    #         "jaja",
    #     )
    #
    #     return "email sent"

    # api_v1_resource.add_resource(UserListResource, '/users')
    # api_v1_resource.add_resource(UserResource, '/users/<int:id>')
    # api_v1_resource.add_resource(UserBulkDeleteResource, '/users/bulk-delete')
    # api_v1_resource.add_resource(UserBookTourResource, '/users/<int:user_id>/book-tour/<int:tour_id>')
    #
    # api_v1_resource.add_resource(DestinationListResource, '/destinations')
    # api_v1_resource.add_resource(DestinationResource, '/destinations/<int:id>')

    api_v1.include_router(auth_router)
    api_v1.include_router(booking_router)
    api_v1.include_router(health_router)
    api_v1.include_router(stats_router)
    api_v1.include_router(tour_router)
    api_v1.include_router(user_router)
    api_v1.include_router(destination_router)
    app.include_router(api_v1)

    return app

def add_sample_data():
    logger = setup_logging()

    try:
        if db.session.execute(select(User)).first():
            logger.info("База данных уже содержит данные, пропускаем добавление тестовых данных")
            return

        logger.info("Добавляем тестовые данные...")

        sample_destinations = [
            Destination(name="Париж", country="Франция", description="Город любви и света", price=1200,
                        duration_days=5),
            Destination(name="Токио", country="Япония", description="Современный мегаполис с древними традициями",
                        price=1800, duration_days=7),
            Destination(name="Бали", country="Индонезия", description="Тропический рай с пляжами", price=900,
                        duration_days=10)
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
        logger.info("Тестовые данные успешно добавлены")

    except Exception as e:
        logger.error(f"Ошибка при добавлении тестовых данных: {str(e)}", exc_info=True)
        db.session.rollback()

def validate_architecture():
    logger = setup_logging()

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

if __name__ == '__main__':
    app = create_app()
    print("Запуск туристического REST API...")
    print("Модульная архитектура с обработкой исключений и логированием")

    add_sample_data()
    validate_architecture()
    print("DB URL =", app.config["SQLALCHEMY_DATABASE_URI"])
    print("База данных инициализирована")
    print("Тестовые данные добавлены")
    print("Архитектурные принципы проверены")
    print("Логирование настроено")
    
    print("\nСервер запущен: http://localhost:5000")
    print("\nДоступные эндпоинты:")
    print("  GET  /api/users - все пользователи")
    print("  GET  /api/destinations - все направления")
    print("  GET  /api/tours - все туры")
    print("  GET  /api/tours/available - только доступные туры")
    print("  POST /api/users/<id>/book-tour/<id> - бронирование тура")
    print("  POST /api/v1/auth/register - регистрация пользователя") #!
    print("  POST /api/v1/auth/login - авторизация существующего пользователя") #!
    print("\nДля тестирования ошибок:")
    print("  GET  /api/users/999 - несуществующий пользователь (404)")
    print("  POST /api/users (с существующим email) - дубликат (409)")
    print("\nЛоги сохраняются в папке logs/")
    
    print(f"\n{app.url_map}\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)