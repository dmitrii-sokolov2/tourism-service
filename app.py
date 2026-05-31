from fastapi import FastAPI, APIRouter
from sqlalchemy import select

from models.models import User, Destination, Tour
from core.database import SessionLocal
from errors.handlers import register_error_handlers

from api.v1.routes.user_routes import user_router
from api.v1.routes.destination_routes import destination_router
from api.v1.routes.auth_routes import auth_router
from api.v1.routes.health_routes import health_router
from api.v1.routes.stats_routes import stats_router
from api.v1.routes.booking_routes import booking_router
from api.v1.routes.tour_routes import tour_router

from core.logging_config import setup_logging
from logging import getLogger

from services.auth_service import hash_password

def create_app():
    app = FastAPI()
    setup_logging()
    logger = getLogger(__name__)

    from fastapi.middleware.cors import CORSMiddleware

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    register_error_handlers(app)

    api_v1 = APIRouter(prefix='/api/v1')

    @api_v1.get('/')
    def index():
        logger.info("GET /")
        # return send_from_directory('static', 'index.html')
        return {"message": "Tourism REST Service"}

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

    api_v1.include_router(auth_router)
    api_v1.include_router(booking_router)
    api_v1.include_router(health_router)
    api_v1.include_router(stats_router)
    api_v1.include_router(tour_router)
    api_v1.include_router(user_router)
    api_v1.include_router(destination_router)

    app.include_router(api_v1)

    @app.on_event("startup")
    def startup_event():
        add_sample_data()

    return app

def add_sample_data():
    db = SessionLocal()
    logger = setup_logging()

    try:
        if db.execute(select(Destination)).first():
            logger.info("База данных уже содержит данные, пропускаем добавление тестовых данных")
            return

        logger.info("Добавляем тестовые данные...")

        sample_destinations = [
            Destination(
                name="Париж",
                country="Франция",
                description="Город любви и света",
                price=1200,
                duration_days=5
            ),
            Destination(
                name="Токио",
                country="Япония",
                description="Современный мегаполис с древними традициями",
                price=1800,
                duration_days=7
            ),
            Destination(
                name="Бали",
                country="Индонезия",
                description="Тропический рай с пляжами",
                price=900,
                duration_days=10
            )
        ]
        for destination in sample_destinations:
            db.add(destination)

        db.commit()

        for destination in sample_destinations:
            db.refresh(destination)

        sample_users = [
            User(
                name="Иван Иванов",
                email="ivan@mail.com",
                phone="+79991234567",
                password_hash=hash_password('12345')
            ),
            User(
                name="Мария Петрова",
                email="maria@mail.com",
                phone="+79997654321",
                password_hash=hash_password('qwerty')
            ),
            User(
                name="Алексей Сидоров",
                email="alex@mail.com",
                phone="+79998887766",
                password_hash=hash_password('hahahehe')
            )
        ]

        for user in sample_users:
            db.add(user)

        db.commit()

        sample_tours = [
            Tour(
                destination_id=sample_destinations[0].id,
                start_date="2024-12-01",
                end_date="2024-12-05",
                available_slots=5
            ),
            Tour(
                destination_id=sample_destinations[1].id,
                start_date="2024-12-10",
                end_date="2024-12-17",
                available_slots=3
            ),
            Tour(
                destination_id=sample_destinations[2].id,
                start_date="2024-12-15",
                end_date="2024-12-25",
                available_slots=8
            )
        ]

        for tour in sample_tours:
            db.add(tour)

        db.commit()
        logger.info("Тестовые данные успешно добавлены")

    except Exception as e:
        logger.error(f"Ошибка при добавлении тестовых данных: {str(e)}", exc_info=True)
        db.rollback()
    finally:
        db.close()

# if __name__ == '__main__':
#     app = create_app()
#     print("Запуск туристического REST API...")
#     print("Модульная архитектура с обработкой исключений и логированием")
#
#     add_sample_data()
#     validate_architecture()
#     print("База данных инициализирована")
#     print("Тестовые данные добавлены")
#     print("Архитектурные принципы проверены")
#     print("Логирование настроено")
#
#     print("\nСервер запущен: http://localhost:5000")
#     print("\nДоступные эндпоинты:")
#     print("  GET  /api/users - все пользователи")
#     print("  GET  /api/destinations - все направления")
#     print("  GET  /api/tours - все туры")
#     print("  GET  /api/tours/available - только доступные туры")
#     print("  POST /api/users/<id>/book-tour/<id> - бронирование тура")
#     print("  POST /api/v1/auth/register - регистрация пользователя") #!
#     print("  POST /api/v1/auth/login - авторизация существующего пользователя") #!
#     print("\nДля тестирования ошибок:")
#     print("  GET  /api/users/999 - несуществующий пользователь (404)")
#     print("  POST /api/users (с существующим email) - дубликат (409)")
#     print("\nЛоги сохраняются в папке logs/")
#
#     print(f"\n{app.url_map}\n")
#
#     app.run(host='0.0.0.0', port=5000, debug=True)