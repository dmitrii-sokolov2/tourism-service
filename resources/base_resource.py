"""
Базовый класс для всех API ресурсов с расширенной обработкой исключений.

Предоставляет общие методы для:
- Обработки исключений в формате Problem Details
- Работы с базой данных в соответствии с SQLAlchemy 2.0
- Единообразного логирования операций

Наследуется всеми ресурсами API для обеспечения
единообразного поведения и обработки ошибок.

Автор: [Соколов Дмитрий] 
Версия: 3.0
"""

from flask_restful import Resource
from flask import request
import logging
import threading

logger = logging.getLogger(__name__)

class BaseResource(Resource):
    """
    Базовый класс для всех API ресурсов с расширенной обработкой исключений.
    
    Методы:
        handle_exception(): Обрабатывает исключения и возвращает Problem Details
        get_by_id(): Получает объект по ID (совместимость с SQLAlchemy 2.0)
        
    Пример использования:
        class UserResource(BaseResource):
            def get(self, id):
                try:
                    user = self.get_by_id(User, id)
                    return user.to_dict()
                except Exception as e:
                    return self.handle_exception(e, "Failed to fetch user")
    """
    
    def handle_exception(self, e, message="Operation failed"):
        """
        Обрабатывает исключения и возвращает ответ в формате Problem Details.
        
        Args:
            e (Exception): Исключение для обработки
            message (str): Сообщение для логирования
            
        Returns:
            tuple: JSON ответ и HTTP статус код
            
        Пример ответа:
            {
                "type": "about:blank",
                "title": "UserNotFoundException", 
                "status": 404,
                "detail": "User with ID 999 not found",
                "instance": "/api/users/999"
            }
        """
        logger.error(f"{message}: {str(e)}")
        
        # Обработка пользовательских исключений
        if hasattr(e, 'status_code') and hasattr(e, 'message'):
            return {
                "type": "about:blank",
                "title": e.__class__.__name__,
                "status": e.status_code,
                "detail": e.message,
                "instance": request.path
            }, e.status_code
        
        # Обработка стандартных исключений
        status_code = 400
        if isinstance(e, ValueError):
            status_code = 422
        elif isinstance(e, KeyError):
            status_code = 400
        
        return {
            "type": "about:blank",
            "title": "Bad Request",
            "status": status_code,
            "detail": str(e),
            "instance": request.path
        }, status_code

    def get_by_id(self, model, id):
        """
        Получает объект из базы данных по ID.
        
        Args:
            model: Класс модели SQLAlchemy
            id (int): ID объекта для поиска
            
        Returns:
            object: Найденный объект или None
            
        Пример:
            user = self.get_by_id(User, 1)
        """
        from models import db  
        return db.session.get(model, id)
    def handle_concurrent_operation(self, operation_func, *args, **kwargs):
        
        """Обработка операций в отдельном потоке"""
        def run_operation():
            try:
                return operation_func(*args, **kwargs)
            except Exception as e:
                return self.handle_exception(e, "Concurrent operation failed")
        
        thread = threading.Thread(target=run_operation)
        thread.start()
        return {"status": "processing", "thread": thread.name}