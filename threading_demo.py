"""
Демонстрация многопоточности для курсовой
"""
import threading
import time
import random
from models import db, User, Tour
from services.tourism_services import ThreadSafeBookingService, TourismExecutorService

def demo_concurrent_bookings():
    """Демо конкурентных бронирований"""
    print("🚀 Запуск демо многопоточного бронирования...")
    
    # Симуляция 10 одновременных бронирований
    users = User.query.limit(3).all()
    tours = Tour.query.limit(2).all()
    
    executor = TourismExecutorService()
    futures = []
    
    for i in range(10):
        user = random.choice(users)
        tour = random.choice(tours)
        future = executor.submit_booking_task(user.id, tour.id)
        futures.append((user.name, tour.id, future))
        print(f"📦 Отправлено бронирование {i+1}: {user.name} -> Тур {tour.id}")
    
    # Ждем результаты
    for user_name, tour_id, future in futures:
        try:
            result = future.result(timeout=10)
            print(f"✅ Успешно: {user_name} забронировал тур {tour_id}")
        except Exception as e:
            print(f"❌ Ошибка: {user_name} - {str(e)}")
    
    print("🎯 Демо завершено!")

if __name__ == "__main__":
    from app import app
    with app.app_context():
        demo_concurrent_bookings()