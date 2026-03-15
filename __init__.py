# Главное приложение
from app import app

# Модели базы данных
from models import db, User, Destination, Tour

# API ресурсы
from resources.user_resources import (
    UserListResource, UserResource, UserBulkDeleteResource, UserBookTourResource
)
from resources.destination_resources import (
    DestinationListResource, DestinationResource
)
from resources.tour_resources import (
    TourListResource, TourResource, AvailableToursResource
)

# Сервисы бизнес-логики
from services.tourism_services import (
    UserService, TourService, DestinationService, BookingService
)

# Исключения из папки exceptions
from exceptions.custom_exceptions import (
    TourismBaseException,
    UserNotFoundException, UserEmailDuplicateException, UserValidationException,
    DestinationNotFoundException, DestinationNameDuplicateException, DestinationValidationException,
    TourNotFoundException, TourValidationException, TourDateException,
    NoAvailableSlotsException, TourNotActiveException, DuplicateBookingException, BookingLimitException
)

# Валидаторы из папки validators
from validators.user_validator import UserValidator
from validators.tour_validator import TourValidator
from validators.destination_validator import DestinationValidator

# ProblemDetails из папки transfer
try:
    from transfer.problem_details import ProblemDetails
except ImportError:
    # Альтернативный способ импорта
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), 'transfer'))
    from problem_details import ProblemDetails

__all__ = [
    # Приложение и БД
    'app', 'db',
    
    # Модели
    'User', 'Destination', 'Tour',
    
    # Ресурсы API
    'UserListResource', 'UserResource', 'UserBulkDeleteResource', 'UserBookTourResource',
    'DestinationListResource', 'DestinationResource',
    'TourListResource', 'TourResource', 'AvailableToursResource',
    
    # Сервисы
    'UserService', 'TourService', 'DestinationService', 'BookingService',
    
    # Формат ошибок
    'ProblemDetails',
    
    # Исключения
    'TourismBaseException',
    'UserNotFoundException', 'UserEmailDuplicateException', 'UserValidationException',
    'DestinationNotFoundException', 'DestinationNameDuplicateException', 'DestinationValidationException',
    'TourNotFoundException', 'TourValidationException', 'TourDateException',
    'NoAvailableSlotsException', 'TourNotActiveException', 'DuplicateBookingException', 'BookingLimitException',
    
    # Валидаторы
    'UserValidator', 'TourValidator', 'DestinationValidator'
]

from services.tourism_services import ThreadSafeBookingService

# Добавить в __all__
'ThreadSafeBookingService'