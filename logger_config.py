"""
Модуль конфигурации системы логирования для туристического REST API.

Этот модуль предоставляет централизованную систему логирования с:
- Разделением логов по модулям (users, tours, destinations)
- Ротацией файлов для предотвращения переполнения диска
- Форматированием с временными метками и контекстом
- Поддержкой разных уровней логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)

Основные компоненты:
- setup_logger(): Функция для создания и настройки логгеров
- Глобальные логгеры для каждого сервиса

Использование:
    from logger_config import user_logger, tour_logger
    user_logger.info("Сообщение для логирования пользователей")

Автор: [Соколов Дмитрий]
Версия: 1.0
"""

import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(name, log_file, level=logging.INFO):
    """
    Создает и настраивает логгер с ротацией файлов.
    
    Args:
        name (str): Имя логгера (обычно __name__ модуля)
        log_file (str): Имя файла для записи логов
        level (int): Уровень логирования (по умолчанию INFO)
    
    Returns:
        logging.Logger: Настроенный объект логгера
    
    Пример:
        logger = setup_logger('user_service', 'users.log')
        logger.info("Тестовое сообщение")
    """
    
    # Создаем папку для логов если её нет
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_path = os.path.join(log_dir, log_file)
    
    # Создаем логгер
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Форматирование
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Обработчик для файла с ротацией
    file_handler = RotatingFileHandler(
        log_path, 
        maxBytes=10485760,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    # Обработчик для консоли
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Добавляем обработчики
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Создаем логгеры для разных модулей
user_logger = setup_logger('user_service', 'users.log')
"""Логгер для сервиса пользователей. Записывает операции с пользователями."""

destination_logger = setup_logger('destination_service', 'destinations.log')
"""Логгер для сервиса направлений. Записывает операции с туристическими направлениями."""

tour_logger = setup_logger('tour_service', 'tours.log')
"""Логгер для сервиса туров. Записывает операции с турами и бронированиями."""

api_logger = setup_logger('api', 'api.log')
"""Логгер для общего API. Записывает HTTP запросы и системные события."""