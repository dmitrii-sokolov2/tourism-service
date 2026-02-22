"""
Модуль пользовательских исключений для туристического REST API.

Содержит иерархию исключений для централизованной обработки ошибок 
в туристическом приложении.

Базовые классы:
    TourismBaseException: Базовое исключение для всех пользовательских исключений

Категории исключений:
    User Exceptions: Ошибки связанные с пользователями
    Destination Exceptions: Ошибки связанные с направлениями  
    Tour Exceptions: Ошибки связанные с турами
    Booking Exceptions: Ошибки связанные с бронированиями

Все исключения наследуются от TourismBaseException и включают:
    - Человеко-читаемые сообщения
    - Соответствующие HTTP статус коды
    - Контекстную информацию об ошибке

Автор: [Соколов Дмитрий]
Версия: 3.0
"""


class TourismBaseException(Exception):
    """
    Базовое исключение для всех пользовательских исключений туристического агентства.
    
    Предоставляет стандартизированный формат для всех исключений приложения.
    
    Атрибуты:
        message (str): Детальное описание ошибки
        status_code (int): HTTP статус код для ответа
        
    Пример:
        >>> raise TourismBaseException("Something went wrong", 500)
    """
    
    def __init__(self, message: str, status_code: int = 422):
        """
        Инициализирует базовое исключение.
        
        Args:
            message (str): Детальное описание ошибки
            status_code (int): HTTP статус код (по умолчанию 400)
        """
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


# =============================================================================
# ИСКЛЮЧЕНИЯ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ (USER)
# =============================================================================

class UserNotFoundException(TourismBaseException):
    """
    Исключение: пользователь не найден.
    
    Вызывается когда запрашиваемый пользователь не существует в системе.
    
    Атрибуты:
        user_id: ID пользователя который не найден
        message: Детальное сообщение об ошибке
        
    Пример:
        >>> raise UserNotFoundException(123)
    """
    
    def __init__(self, user_id: int, message: str = None):
        """
        Инициализирует исключение пользователь не найден.
        
        Args:
            user_id (int): ID пользователя который не найден
            message (str, optional): Кастомное сообщение об ошибке
        """
        if message is None:
            message = f"Пользователь с ID {user_id} не найден"
        super().__init__(message, 404)


class UserEmailDuplicateException(TourismBaseException):
    """
    Исключение: пользователь с таким email уже существует.
    
    Вызывается при попытке создать пользователя с уже существующим email.
    
    Атрибуты:
        email: Email который уже используется
        message: Детальное сообщение об ошибке
        
    Пример:
        >>> raise UserEmailDuplicateException("test@mail.com")
    """
    
    def __init__(self, email: str, message: str = None):
        """
        Инициализирует исключение дублирования email.
        
        Args:
            email (str): Email который уже используется
            message (str, optional): Кастомное сообщение об ошибке
        """
        if message is None:
            message = f"Пользователь с email '{email}' уже существует"
        super().__init__(message, 409)


class UserValidationException(TourismBaseException):
    """
    Исключение: ошибка валидации данных пользователя.
    
    Вызывается когда данные пользователя не проходят валидацию.
    
    Атрибуты:
        field: Поле в котором ошибка
        value: Некорректное значение
        message: Детальное сообщение об ошибке
        
    Пример:
        >>> raise UserValidationException("email", "invalid", "Invalid format")
    """
    
    def __init__(self, field: str, value: any, message: str = None):
        """
        Инициализирует исключение валидации пользователя.
        
        Args:
            field (str): Поле в котором ошибка
            value (any): Некорректное значение
            message (str, optional): Кастомное сообщение об ошибке
        """
        if message is None:
            message = f"Некорректное значение '{value}' для поля '{field}'"
        super().__init__(message, 422)


# =============================================================================
# ИСКЛЮЧЕНИЯ ДЛЯ НАПРАВЛЕНИЙ (DESTINATION)
# =============================================================================

class DestinationNotFoundException(TourismBaseException):
    """
    Исключение: направление не найдено.
    
    Вызывается когда запрашиваемое направление не существует в системе.
    
    Атрибуты:
        destination_id: ID направления которое не найдено
        message: Детальное сообщение об ошибке
        
    Пример:
        >>> raise DestinationNotFoundException(456)
    """
    
    def __init__(self, destination_id: int, message: str = None):
        """
        Инициализирует исключение направление не найдено.
        
        Args:
            destination_id (int): ID направления которое не найдено
            message (str, optional): Кастомное сообщение об ошибке
        """
        if message is None:
            message = f"Направление с ID {destination_id} не найдено"
        super().__init__(message, 404)


class DestinationNameDuplicateException(TourismBaseException):
    """
    Исключение: направление с таким названием уже существует.
    
    Вызывается при попытке создать направление с уже существующим названием в стране.
    
    Атрибуты:
        name: Название направления
        country: Страна направления
        message: Детальное сообщение об ошибке
        
    Пример:
        >>> raise DestinationNameDuplicateException("Париж", "Франция")
    """
    
    def __init__(self, name: str, country: str, message: str = None):
        """
        Инициализирует исключение дублирования названия направления.
        
        Args:
            name (str): Название направления
            country (str): Страна направления
            message (str, optional): Кастомное сообщение об ошибке
        """
        if message is None:
            message = f"Направление с названием '{name}' в стране '{country}' уже существует"
        super().__init__(message, 409)


class DestinationValidationException(TourismBaseException):
    """
    Исключение: ошибка валидации данных направления.
    
    Вызывается когда данные направления не проходят валидацию.
    
    Атрибуты:
        field: Поле в котором ошибка
        value: Некорректное значение
        message: Детальное сообщение об ошибке
        
    Пример:
        >>> raise DestinationValidationException("price", -100, "Price cannot be negative")
    """
    
    def __init__(self, field: str, value: any, message: str = None):
        """
        Инициализирует исключение валидации направления.
        
        Args:
            field (str): Поле в котором ошибка
            value (any): Некорректное значение
            message (str, optional): Кастомное сообщение об ошибке
        """
        if message is None:
            message = f"Некорректное значение '{value}' для поля направления '{field}'"
        super().__init__(message, 422)


# =============================================================================
# ИСКЛЮЧЕНИЯ ДЛЯ ТУРОВ (TOUR)
# =============================================================================

class TourNotFoundException(TourismBaseException):
    """
    Исключение: тур не найден.
    
    Вызывается когда запрашиваемый тур не существует в системе.
    
    Атрибуты:
        tour_id: ID тура который не найден
        message: Детальное сообщение об ошибке
        
    Пример:
        >>> raise TourNotFoundException(789)
    """
    
    def __init__(self, tour_id: int, message: str = None):
        """
        Инициализирует исключение тур не найден.
        
        Args:
            tour_id (int): ID тура который не найден
            message (str, optional): Кастомное сообщение об ошибке
        """
        if message is None:
            message = f"Тур с ID {tour_id} не найден"
        super().__init__(message, 404)


class TourValidationException(TourismBaseException):
    """
    Исключение: ошибка валидации данных тура.
    
    Вызывается когда данные тура не проходят валидацию.
    
    Атрибуты:
        field: Поле в котором ошибка
        value: Некорректное значение
        message: Детальное сообщение об ошибке
        
    Пример:
        >>> raise TourValidationException("available_slots", -5, "Slots cannot be negative")
    """
    
    def __init__(self, field: str, value: any, message: str = None):
        """
        Инициализирует исключение валидации тура.
        
        Args:
            field (str): Поле в котором ошибка
            value (any): Некорректное значение
            message (str, optional): Кастомное сообщение об ошибке
        """
        if message is None:
            message = f"Некорректное значение '{value}' для поля тура '{field}'"
        super().__init__(message, 422)


class TourDateException(TourismBaseException):
    """
    Исключение: некорректные даты тура.
    
    Вызывается когда дата окончания тура раньше или равна дате начала.
    
    Атрибуты:
        start_date: Дата начала тура
        end_date: Дата окончания тура
        message: Детальное сообщение об ошибке
        
    Пример:
        >>> raise TourDateException("2024-01-01", "2023-12-31")
    """
    
    def __init__(self, start_date: str, end_date: str, message: str = None):
        """
        Инициализирует исключение некорректных дат тура.
        
        Args:
            start_date (str): Дата начала тура
            end_date (str): Дата окончания тура
            message (str, optional): Кастомное сообщение об ошибке
        """
        if message is None:
            message = f"Дата окончания '{end_date}' должна быть позже даты начала '{start_date}'"
        super().__init__(message, 422)


# =============================================================================
# ИСКЛЮЧЕНИЯ ДЛЯ БРОНИРОВАНИЙ (BOOKING)
# =============================================================================

class BookingException(TourismBaseException):
    """
    Базовое исключение для ошибок бронирования.
    
    Родительский класс для всех исключений связанных с бронированиями.
    
    Пример:
        >>> raise BookingException("Booking failed")
    """
    pass


class NoAvailableSlotsException(BookingException):
    """
    Исключение: нет доступных мест для бронирования.
    
    Вызывается когда в туре недостаточно свободных мест для бронирования.
    
    Атрибуты:
        tour_id: ID тура
        available_slots: Количество доступных мест
        message: Детальное сообщение об ошибке
        
    Пример:
        >>> raise NoAvailableSlotsException(789, 0)
    """
    
    def __init__(self, tour_id: int, available_slots: int, message: str = None):
        """
        Инициализирует исключение отсутствия доступных мест.
        
        Args:
            tour_id (int): ID тура
            available_slots (int): Количество доступных мест
            message (str, optional): Кастомное сообщение об ошибке
        """
        if message is None:
            message = f"В туре {tour_id} нет доступных мест. Доступно: {available_slots}"
        super().__init__(message, 403)


class TourNotActiveException(BookingException):
    """
    Исключение: тур не активен для бронирования.
    
    Вызывается когда попытка забронировать неактивный тур.
    
    Атрибуты:
        tour_id: ID неактивного тура
        message: Детальное сообщение об ошибке
        
    Пример:
        >>> raise TourNotActiveException(789)
    """
    
    def __init__(self, tour_id: int, message: str = None):
        """
        Инициализирует исключение неактивного тура.
        
        Args:
            tour_id (int): ID неактивного тура
            message (str, optional): Кастомное сообщение об ошибке
        """
        if message is None:
            message = f"Тур {tour_id} не активен для бронирования"
        super().__init__(message, 403)


class DuplicateBookingException(BookingException):
    """
    Исключение: повторное бронирование того же тура.
    
    Вызывается когда пользователь пытается забронировать уже забронированный тур.
    
    Атрибуты:
        user_id: ID пользователя
        tour_id: ID тура
        message: Детальное сообщение об ошибке
        
    Пример:
        >>> raise DuplicateBookingException(123, 789)
    """
    
    def __init__(self, user_id: int, tour_id: int, message: str = None):
        """
        Инициализирует исключение дублирования бронирования.
        
        Args:
            user_id (int): ID пользователя
            tour_id (int): ID тура
            message (str, optional): Кастомное сообщение об ошибке
        """
        if message is None:
            message = f"Пользователь {user_id} уже забронировал тур {tour_id}"
        super().__init__(message, 409)


class BookingLimitException(BookingException):
    """
    Исключение: превышен лимит бронирований.
    
    Вызывается когда пользователь превышает максимальное разрешенное количество бронирований.
    
    Атрибуты:
        user_id: ID пользователя
        current_count: Текущее количество бронирований
        max_limit: Максимальный лимит бронирований
        message: Детальное сообщение об ошибке
        
    Пример:
        >>> raise BookingLimitException(123, 5, 5)
    """
    
    def __init__(self, user_id: int, current_count: int, max_limit: int, message: str = None):
        """
        Инициализирует исключение превышения лимита бронирований.
        
        Args:
            user_id (int): ID пользователя
            current_count (int): Текущее количество бронирований
            max_limit (int): Максимальный лимит бронирований
            message (str, optional): Кастомное сообщение об ошибке
        """
        if message is None:
            message = f"Пользователь {user_id} уже имеет {current_count} бронирований. Максимум: {max_limit}"
        super().__init__(message, 403)