import unittest
import json
import os
import sys
from datetime import datetime

# Добавляем текущую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, User, Destination, Tour

class TourismAPITestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        
        with app.app_context():
            db.create_all()
            self.add_test_data()
    
    def add_test_data(self):
        """Добавляем тестовые данные"""
        # Очищаем базу
        db.session.query(User).delete()
        db.session.query(Destination).delete()
        db.session.query(Tour).delete()
        
        # Тестовые направления
        dest1 = Destination(name="Тестовый Париж", country="Франция", description="Тест", price=1000, duration_days=5)
        dest2 = Destination(name="Тестовый Токио", country="Япония", description="Тест", price=1500, duration_days=7)
        db.session.add(dest1)
        db.session.add(dest2)
        
        # Тестовые пользователи
        user1 = User(name="Тест Иванов", email="test1@mail.com", phone="+79990000001")
        user2 = User(name="Тест Петрова", email="test2@mail.com", phone="+79990000002")
        db.session.add(user1)
        db.session.add(user2)
        
        # Тестовые туры
        tour1 = Tour(destination_id=1, start_date="2024-12-01", end_date="2024-12-05", available_slots=5)
        tour2 = Tour(destination_id=2, start_date="2024-12-10", end_date="2024-12-17", available_slots=3)
        db.session.add(tour1)
        db.session.add(tour2)
        
        db.session.commit()
    
    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    # Тесты для User
    def test_get_users(self):
        response = self.app.get('/api/users')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
    
    def test_create_user(self):
        user_data = {
            "name": "Новый Тест",
            "email": "newtest@mail.com",
            "phone": "+79990000003"
        }
        response = self.app.post(
            '/api/users',
            data=json.dumps(user_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['name'], "Новый Тест")
        self.assertEqual(data['email'], "newtest@mail.com")
    
    def test_get_user_by_id(self):
        response = self.app.get('/api/users/1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['id'], 1)
    
    def test_update_user(self):
        update_data = {
            "name": "Обновленное Имя",
            "phone": "+79991111111"
        }
        response = self.app.put(
            '/api/users/1',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], "Обновленное Имя")
    
    def test_delete_user(self):
        response = self.app.delete('/api/users/1')
        self.assertEqual(response.status_code, 200)
        
        # Проверяем что пользователь удален
        response = self.app.get('/api/users/1')
        self.assertEqual(response.status_code, 404)
    
    def test_bulk_delete_users(self):
        delete_data = {
            "user_ids": [1, 2]
        }
        response = self.app.delete(
            '/api/users/bulk-delete',
            data=json.dumps(delete_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
    
    # Тесты для Destination
    def test_get_destinations(self):
        response = self.app.get('/api/destinations')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
    
    def test_create_destination(self):
        dest_data = {
            "name": "Новое Направление",
            "country": "Тестовая Страна",
            "description": "Тестовое описание",
            "price": 2000,
            "duration_days": 8
        }
        response = self.app.post(
            '/api/destinations',
            data=json.dumps(dest_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['name'], "Новое Направление")
    
    # Тесты для Tour
    def test_get_tours(self):
        response = self.app.get('/api/tours')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
    
    def test_create_tour(self):
        tour_data = {
            "destination_id": 1,
            "start_date": "2024-12-20",
            "end_date": "2024-12-25",
            "available_slots": 10,
            "is_active": True
        }
        response = self.app.post(
            '/api/tours',
            data=json.dumps(tour_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['destination_id'], 1)
    
    # Тест бронирования тура
    def test_book_tour(self):
        response = self.app.post('/api/users/1/book-tour/1')
        self.assertEqual(response.status_code, 200) 

    def test_duplicate_email(self):
        self.assertEqual(response.status_code, 409)

    def test_update_user(self):
        # Добавляем email в данные обновления
        update_data = {
            "name": "Обновленное Имя",
            "email": "test1@mail.com",  # Добавляем обязательный email
            "phone": "+79991111111"
        }
    
    # Тесты обработки ошибок
    def test_user_not_found(self):
        response = self.app.get('/api/users/999')
        self.assertEqual(response.status_code, 404)
    
    def test_invalid_json(self):
        response = self.app.post(
            '/api/users',
            data="invalid json",
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_duplicate_email(self):
        user_data = {
            "name": "Дубликат",
            "email": "test1@mail.com", 
            "phone": "+79990000004"
        }
        response = self.app.post(
            '/api/users',
            data=json.dumps(user_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 409)

if __name__ == '__main__':
    # Запуск тестов с подробным выводом
    unittest.main(verbosity=2)