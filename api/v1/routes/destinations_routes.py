from flask import Blueprint, jsonify

from models.models import Destination
from core.logging_config import setup_logging

destinations_bp = Blueprint('destinations', __name__)
logger = setup_logging()

@destinations_bp.route('/coordinates')
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
                    'price': f'{price_in_rubles}'
                })
        
        if not result:
            result = [
                {'id': 1, 'name': 'Париж', 'country': 'Франция', 'lat': 48.8566, 'lng': 2.3522, 'tours': 5, 'price': '60000'},
                {'id': 2, 'name': 'Токио', 'country': 'Япония', 'lat': 35.6762, 'lng': 139.6503, 'tours': 3, 'price': '90000'},
                {'id': 3, 'name': 'Бали', 'country': 'Индонезия', 'lat': -8.3405, 'lng': 115.0920, 'tours': 8, 'price': '45000'}
            ]
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Ошибка в /api/v1/destinations/coordinates: {str(e)}")
        import traceback
        traceback.print_exc()
        
        test_data = [
            {'id': 1, 'name': 'Париж', 'country': 'Франция', 'lat': 48.8566, 'lng': 2.3522, 'tours': 5, 'price': '60000'},
            {'id': 2, 'name': 'Токио', 'country': 'Япония', 'lat': 35.6762, 'lng': 139.6503, 'tours': 3, 'price': '90000'},
            {'id': 3, 'name': 'Бали', 'country': 'Индонезия', 'lat': -8.3405, 'lng': 115.0920, 'tours': 8, 'price': '45000'}
        ]
        return jsonify(test_data)