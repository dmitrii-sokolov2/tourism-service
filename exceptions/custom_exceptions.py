class TourismBaseException(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)
        
class UserNotFoundException(TourismBaseException):
    def __init__(self, user_id: int, message: str = None):

        if message is None:
            message = f"Пользователь с ID {user_id} не найден"
        super().__init__(message, 404)


class UserEmailDuplicateException(TourismBaseException):
    def __init__(self, email: str, message: str = None):
        if message is None:
            message = f"Пользователь с email '{email}' уже существует"
        super().__init__(message, 409)


class UserValidationException(TourismBaseException): 
    def __init__(self, field: str, value: any, message: str = None):
        if message is None:
            message = f"Некорректное значение '{value}' для поля '{field}'"
        super().__init__(message, 422)

class DestinationNotFoundException(TourismBaseException):
    def __init__(self, destination_id: int, message: str = None):
        if message is None:
            message = f"Направление с ID {destination_id} не найдено"
        super().__init__(message, 404)


class DestinationNameDuplicateException(TourismBaseException):
    def __init__(self, name: str, country: str, message: str = None):
        if message is None:
            message = f"Направление с названием '{name}' в стране '{country}' уже существует"
        super().__init__(message, 409)


class DestinationValidationException(TourismBaseException):
    def __init__(self, field: str, value: any, message: str = None):
        if message is None:
            message = f"Некорректное значение '{value}' для поля направления '{field}'"
        super().__init__(message, 422)

class TourNotFoundException(TourismBaseException):
    def __init__(self, tour_id: int, message: str = None):
        if message is None:
            message = f"Тур с ID {tour_id} не найден"
        super().__init__(message, 404)


class TourValidationException(TourismBaseException):
    def __init__(self, field: str, value: any, message: str = None):
        if message is None:
            message = f"Некорректное значение '{value}' для поля тура '{field}'"
        super().__init__(message, 422)


class TourDateException(TourismBaseException):
    def __init__(self, start_date: str, end_date: str, message: str = None):
        if message is None:
            message = f"Дата окончания '{end_date}' должна быть позже даты начала '{start_date}'"
        super().__init__(message, 422)

class BookingException(TourismBaseException):
    pass


class NoAvailableSlotsException(BookingException):
    def __init__(self, tour_id: int, available_slots: int, message: str = None):
        if message is None:
            message = f"В туре {tour_id} нет доступных мест. Доступно: {available_slots}"
        super().__init__(message, 403)


class TourNotActiveException(BookingException):
    def __init__(self, tour_id: int, message: str = None):
        if message is None:
            message = f"Тур {tour_id} не активен для бронирования"
        super().__init__(message, 403)


class DuplicateBookingException(BookingException):
    def __init__(self, user_id: int, tour_id: int, message: str = None):

        if message is None:
            message = f"Пользователь {user_id} уже забронировал тур {tour_id}"
        super().__init__(message, 409)


class BookingLimitException(BookingException):
    def __init__(self, user_id: int, current_count: int, max_limit: int, message: str = None):
        if message is None:
            message = f"Пользователь {user_id} уже имеет {current_count} бронирований. Максимум: {max_limit}"
        super().__init__(message, 403)