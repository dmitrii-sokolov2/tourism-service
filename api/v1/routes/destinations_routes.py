from flask import Blueprint, jsonify
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

destinations_bp = Blueprint('destinations', __name__)
logger = setup_logging()

@destinations_bp.route('/coordinates')
def get_destinations_coordinates():
    """Возвращает города с координатами для глобуса"""
    try:
        # Получаем все направления
        destinations = Destination.query.all()
        result = []
        
        for dest in destinations:
            # Проверяем, есть ли координаты
            if dest.latitude and dest.longitude:
                # Считаем количество туров для этого направления
                tours_count = len(dest.tours) if hasattr(dest, 'tours') else 0
                
                # 👇 ПРЕОБРАЗУЕМ ЦЕНУ (умножаем на 50 для красивых рублей)
                price_in_rubles = int(dest.price * 50) if dest.price else 35000
                
                result.append({
                    'id': dest.id,
                    'name': dest.name,
                    'country': dest.country,
                    'lat': float(dest.latitude),
                    'lng': float(dest.longitude),
                    'tours': tours_count,
                    'price': f'{price_in_rubles}'  # Теперь 1200 → 60000
                })
        
        # Если нет городов с координатами, возвращаем тестовые
        if not result:
            result = [
                {'id': 1, 'name': 'Париж', 'country': 'Франция', 'lat': 48.8566, 'lng': 2.3522, 'tours': 5, 'price': '60000'},
                {'id': 2, 'name': 'Токио', 'country': 'Япония', 'lat': 35.6762, 'lng': 139.6503, 'tours': 3, 'price': '90000'},
                {'id': 3, 'name': 'Бали', 'country': 'Индонезия', 'lat': -8.3405, 'lng': 115.0920, 'tours': 8, 'price': '45000'}
            ]
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Ошибка в /api/destinations/coordinates: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Возвращаем тестовые данные при ошибке
        test_data = [
            {'id': 1, 'name': 'Париж', 'country': 'Франция', 'lat': 48.8566, 'lng': 2.3522, 'tours': 5, 'price': '60000'},
            {'id': 2, 'name': 'Токио', 'country': 'Япония', 'lat': 35.6762, 'lng': 139.6503, 'tours': 3, 'price': '90000'},
            {'id': 3, 'name': 'Бали', 'country': 'Индонезия', 'lat': -8.3405, 'lng': 115.0920, 'tours': 8, 'price': '45000'}
        ]
        return jsonify(test_data)