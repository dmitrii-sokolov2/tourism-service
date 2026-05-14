from models.models import Destination, Tour, User
from exceptions.custom_exceptions import *
from logger_config import user_logger, destination_logger, tour_logger
from threading import Lock, BoundedSemaphore
from sqlalchemy.orm import Session
from sqlalchemy import select
from core.database import SessionLocal

class TourService:
    @staticmethod
    def validate_tour_creation(data, db: Session):
        if not data.get('destination_id'):
            raise TourValidationException('destination_id', data.get('destination_id'), "ID направления обязательно")
        
        if data.get('available_slots', 0) < 0:
            raise TourValidationException('available_slots', data.get('available_slots'), "Количество мест не может быть отрицательным")
        
        destination = db.get(Destination, data.get('destination_id'))
        if not destination:
            raise DestinationNotFoundException(data.get('destination_id'))
        
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        if start_date and end_date:
            from datetime import datetime
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                end = datetime.strptime(end_date, '%Y-%m-%d')
                if end <= start:
                    raise TourDateException(start_date, end_date)
            except ValueError:
                raise TourValidationException('dates', f"{start_date}/{end_date}", "Некорректный формат дат. Используйте YYYY-MM-DD")
    
    @staticmethod
    def get_tour_by_id(tour_id, db: Session):
        tour_logger.debug(f"Поиск тура по ID: {tour_id}")
        tour = db.get(Tour, tour_id)
        if not tour:
            tour_logger.warning(f"Тур с ID {tour_id} не найден")
            raise TourNotFoundException(tour_id)
        tour_logger.debug(f"Тур найден: {tour.id} для направления {tour.destination.name}")
        return tour
    
    @staticmethod
    def get_available_tours(db: Session):
        tour_logger.debug("Получение списка доступных туров")

        stmt = select(Tour).where(
            Tour.available_slots > 0,
            Tour.is_active == True
        )

        return db.execute(stmt).scalars().all()


    @staticmethod
    def decrease_available_slots(tour, count=1):
        if tour.available_slots < count:
            raise NoAvailableSlotsException(tour.id, tour.available_slots)
        tour.available_slots -= count
        tour_logger.info(
            f"Уменьшены доступные места в туре {tour.id}: {tour.available_slots + count} -> {tour.available_slots}"
        )

        return tour


class BookingService:
    MAX_BOOKINGS_PER_USER = 5
    
    @staticmethod
    def can_book_tour(user, tour):
        if not user:
            raise UserNotFoundException(None, "Пользователь не указан")
        if not tour:
            raise TourNotFoundException(None, "Тур не указан")
        
        if tour.available_slots <= 0:
            raise NoAvailableSlotsException(tour.id, tour.available_slots)
        
        if not tour.is_active:
            raise TourNotActiveException(tour.id)
        
        if tour in user.booked_tours:
            raise DuplicateBookingException(user.id, tour.id)
        
        if len(user.booked_tours) >= BookingService.MAX_BOOKINGS_PER_USER:
            raise BookingLimitException(user.id, len(user.booked_tours), BookingService.MAX_BOOKINGS_PER_USER)
    
    @staticmethod
    def create_booking(user, tour):
        BookingService.can_book_tour(user, tour)
        TourService.decrease_available_slots(tour)
        user.booked_tours.append(tour)
        
        user_logger.info(f"Пользователь {user.name} забронировал тур {tour.id}")
        tour_logger.info(f"Тур {tour.id} забронирован пользователем {user.name}")
        
        return {
            'user': user,
            'tour': tour,
            'message': 'Тур успешно забронирован'
        }


class UserService:
    @staticmethod
    def validate_user_data(
            data,
            db: Session,
            existing_user=None
    ):

        if not data.get('name'):
            raise UserValidationException('name', data.get('name'), "Имя пользователя обязательно")
        
        if not data.get('email'):
            raise UserValidationException('email', data.get('email'), "Email пользователя обязателен")
        
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data.get('email', '')):
            raise UserValidationException('email', data.get('email'), "Некорректный формат email")

        stmt = select(User).where(
            User.email == data.get('email')
        )
        existing_email = db.execute(stmt).scalar_one_or_none()

        if existing_email and (not existing_user or existing_user.id != existing_email.id):
            raise UserEmailDuplicateException(data.get('email'))

    @staticmethod
    def get_user_by_id(user_id, db: Session):
        user_logger.debug(f"Поиск пользователя по ID: {user_id}")
        user = db.get(User, user_id)

        if not user:
            user_logger.warning(f"Пользователь с ID {user_id} не найден")

            raise UserNotFoundException(user_id)

        user_logger.debug(f"Пользователь найден: {user.name} (ID: {user.id})")

        return user

class DestinationService:
    @staticmethod
    def validate_destination_data(data, existing_destination=None):
        if not data.get('name'):
            raise DestinationValidationException('name', data.get('name'), "Название направления обязательно")
        
        if not data.get('country'):
            raise DestinationValidationException('country', data.get('country'), "Страна направления обязательна")
        
        if data.get('price', 0) < 0:
            raise DestinationValidationException('price', data.get('price'), "Цена не может быть отрицательной")
        
        if data.get('duration_days', 0) <= 0:
            raise DestinationValidationException('duration_days', data.get('duration_days'), "Продолжительность должна быть положительной")

        db = SessionLocal()

        stmt = select(Destination).where(
            Destination.name == data.get('name'),
            Destination.country == data.get('country')
        )

        existing_dest = db.execute(stmt).scalar_one_or_none()
        
        if existing_dest and (not existing_destination or existing_destination.id != existing_dest.id):
            raise DestinationNameDuplicateException(data.get('name'), data.get('country'))

        db.close()

    @staticmethod
    def get_destination_by_id(destination_id, db: Session):
        destination_logger.debug(f"Поиск направления по ID: {destination_id}")
        destination = db.get(Destination, destination_id)
        if not destination:
            destination_logger.warning(f"Направление с ID {destination_id} не найдено")
            raise DestinationNotFoundException(destination_id)
        destination_logger.debug(f"Направление найдено: {destination.name} (ID: {destination.id})")
        return destination

class ThreadSafeBookingService:  
    _booking_locks = {}
    _lock_dict_lock = Lock()
    _booking_semaphore = BoundedSemaphore(5)
    
    @classmethod
    def thread_safe_booking(cls, user, tour):
        with cls._booking_semaphore:
            tour_lock = cls._get_tour_lock(tour.id)
            with tour_lock:
                return BookingService.create_booking(user, tour)
    
    @classmethod
    def _get_tour_lock(cls, tour_id):
        with cls._lock_dict_lock:
            if tour_id not in cls._booking_locks:
                cls._booking_locks[tour_id] = Lock()
            return cls._booking_locks[tour_id]

class TourismExecutorService:
    @staticmethod
    def execute_concurrent_operation(operation_func, *args, **kwargs):
        import threading
        result_container = []
        exception_container = []
        def worker():
            try:
                result = operation_func(*args, **kwargs)
                result_container.append(result)
            except Exception as e:
                exception_container.append(e)
        
        thread = threading.Thread(target=worker)
        thread.start()
        thread.join()
        if exception_container:
            raise exception_container[0]
        return result_container[0] if result_container else None
