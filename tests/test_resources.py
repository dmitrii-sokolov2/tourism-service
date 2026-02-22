"""
Тесты для REST API ресурсов.
"""
import json
import pytest

# --- Тесты UserResource ---
def test_get_users(client, sample_data):
    """Тест получения списка пользователей."""
    response = client.get('/api/users')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]['name'] == "Тестовый Пользователь"

def test_create_user_valid(client):
    """Тест создания пользователя с валидными данными."""
    user_data = {
        "name": "Новый Тестовый Пользователь",
        "email": "newtest@example.com",
        "phone": "+79998887766"
    }
    
    response = client.post(
        '/api/users',
        data=json.dumps(user_data),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['name'] == user_data['name']
    assert data['email'] == user_data['email']

def test_create_user_invalid_json(client):
    """Тест создания пользователя с некорректным JSON."""
    response = client.post(
        '/api/users',
        data="{invalid json",
        content_type='application/json'
    )
    assert response.status_code == 400

def test_get_user_by_id_success(client, sample_data):
    """Тест получения пользователя по ID."""
    response = client.get('/api/users/1')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['id'] == 1
    assert 'email' in data

def test_get_user_by_id_not_found(client):
    """Тест получения несуществующего пользователя."""
    response = client.get('/api/users/999')
    assert response.status_code == 404

def test_update_user_success(client, sample_data):
    """Тест обновления пользователя."""
    update_data = {
        "name": "Обновленное Имя",
        "email": "test@mail.com",  # ← ДОБАВЛЕНО email
        "phone": "+79991111111"
    }
    
    response = client.put(
        '/api/users/1',
        data=json.dumps(update_data),
        content_type='application/json'
    )
    
    assert response.status_code == 200  # ← Теперь должно быть 200
    data = json.loads(response.data)
    assert data['name'] == "Обновленное Имя"
    assert data['phone'] == "+79991111111"

def test_delete_user_success(client, sample_data):
    """Тест удаления пользователя."""
    response = client.delete('/api/users/1')
    assert response.status_code == 200
    
    # Проверяем что пользователь действительно удален
    response = client.get('/api/users/1')
    assert response.status_code == 404

# --- Тесты DestinationResource ---
def test_get_destinations(client, sample_data):
    """Тест получения списка направлений."""
    response = client.get('/api/destinations')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) > 0

def test_create_destination_valid(client):
    """Тест создания направления."""
    dest_data = {
        "name": "Новое Тестовое Направление",
        "country": "Тестовая Страна",
        "description": "Тестовое описание",
        "price": 2000.0,
        "duration_days": 7
    }
    
    response = client.post(
        '/api/destinations',
        data=json.dumps(dest_data),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['name'] == dest_data['name']

def test_create_destination_missing_required(client):
    """Тест создания направления без обязательных полей."""
    dest_data = {
        "name": "Только имя",
        "price": 1000.0
    }
    
    response = client.post(
        '/api/destinations',
        data=json.dumps(dest_data),
        content_type='application/json'
    )
    
    assert response.status_code == 400

# --- Тесты TourResource ---
def test_get_tours(client, sample_data):
    """Тест получения списка туров."""
    response = client.get('/api/tours')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) > 0

def test_get_available_tours(client, sample_data):
    """Тест получения доступных туров."""
    response = client.get('/api/tours/available')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert isinstance(data, list)
    # Все возвращенные туры должны быть активны и иметь места
    for tour in data:
        assert tour['available_slots'] > 0
        assert tour['is_active'] == True

def test_book_tour_success(client, sample_data):
    """Тест успешного бронирования тура."""
    response = client.post('/api/users/1/book-tour/1')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'message' in data
    assert data['message'] == 'Тур успешно забронирован (потокобезопасно)'