
from flask_restful import Resource
from flask import request
import logging
import threading

logger = logging.getLogger(__name__)

class BaseResource(Resource):
    def handle_exception(self, e, message="Operation failed"):
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
        from models import db  
        return db.session.get(model, id)
    def handle_concurrent_operation(self, operation_func, *args, **kwargs):
        def run_operation():
            try:
                return operation_func(*args, **kwargs)
            except Exception as e:
                return self.handle_exception(e, "Concurrent operation failed")
        
        thread = threading.Thread(target=run_operation)
        thread.start()
        return {"status": "processing", "thread": thread.name}