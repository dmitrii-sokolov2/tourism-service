from flask import jsonify, request
import logging
from werkzeug.exceptions import HTTPException
from exceptions import TourismBaseException

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_exception(e):
        logger.error(f"HTTP Error {e.code}: {e.description}")
        
        response = {
            "type": "about:blank",
            "title": e.name,
            "status": e.code,
            "detail": e.description,
            "instance": request.path
        }
        
        return jsonify(response), e.code

    @app.errorhandler(TourismBaseException)
    def handle_custom_exception(e):
        logger.error(f"Custom exception {e.status_code}: {e.message}")
        
        response = {
            "type": "about:blank",
            "title": e.__class__.__name__,
            "status": e.status_code,
            "detail": e.message,
            "instance": request.path
        }
        
        return jsonify(response), e.status_code

    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        
        response = {
            "type": "about:blank",
            "title": "Internal Server Error",
            "status": 500,
            "detail": "An unexpected error occurred",
            "instance": request.path
        }
        
        return jsonify(response), 500