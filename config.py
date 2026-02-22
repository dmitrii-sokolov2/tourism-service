# config.py
import os

# Настройка базы данных
base_dir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(base_dir, 'data', 'tourism.db')

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://tourist:123@localhost/tourism_db?client_encoding=utf8'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'tourism-secret-key-2024'
    
    # НАСТРОЙКИ МНОГОПОТОЧНОСТИ
    MAX_THREAD_POOL_WORKERS = 10
    MAX_CONCURRENT_BOOKINGS = 5
    THREAD_TIMEOUT_SECONDS = 30
    DB_CONNECTION_POOL_SIZE = 20