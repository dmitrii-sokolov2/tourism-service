from flask import Blueprint, jsonify, request
from services.tourism_services import UserService, TourService, BookingService
from models import db
import logging, logging.config
import yaml

def setup_logging():
    """
    Настраивает логирование из YAML конфигурационного файла.
    
    Returns:
        logging.Logger: Настроенный логгер
        
    Raises:
        FileNotFoundError: Если файл конфигурации не найден
        
    Пример:
        >>> logger = setup_logging()
        >>> logger.info("Логирование настроено")
    """
    try:
        with open('logging_config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        logging.config.dictConfig(config)
        logger = logging.getLogger(__name__)
        logger.info("✅ Логирование настроено из YAML конфигурации")
        return logger
    except FileNotFoundError:
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger = logging.getLogger(__name__)
        logger.warning("⚠️ Файл конфигурации логирования не найден, используется базовая настройка")
        return logger

booking_bp = Blueprint('booking', __name__)
logger = setup_logging()

@booking_bp.route('/bulk', methods=['POST'])
def bulk_bookings():
    """Упрощенное массовое бронирование"""
    try:
        data = request.get_json()
        bookings = data.get('bookings', [])
        results = []
        for booking in bookings:
            try:
                # Используем синхронное бронирование для надежности
                user_id = booking['user_id']
                tour_id = booking['tour_id']
                
                user = UserService.get_user_by_id(user_id)
                tour = TourService.get_tour_by_id(tour_id)
                
                result = BookingService.create_booking(user, tour)
                db.session.commit()
                
                results.append({
                    "status": "success", 
                    "user_id": user_id, 
                    "tour_id": tour_id,
                    "message": "Бронирование успешно"
                })
            except Exception as e:
                db.session.rollback()
                results.append({
                    "status": "error", 
                    "user_id": booking.get('user_id'), 
                    "tour_id": booking.get('tour_id'),
                    "error": str(e)
                })
        
        return jsonify({"results": results})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500  