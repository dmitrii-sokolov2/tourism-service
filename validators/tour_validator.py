"""
Модуль валидации данных туров с использованием JSON Schema.

Содержит класс TourValidator для валидации данных туров
по предопределенным схемам в формате JSON Schema.

Основные возможности:
- Валидация данных при создании тура
- Валидация данных при обновлении тура
- Проверка корректности дат и числовых значений
- Детализированные сообщения об ошибках валидации

Особенности валидации туров:
- Проверка дат (start_date, end_date)
- Валидация available_slots (неотрицательные значения)
- Проверка корректности destination_id
- Валидация цен и статусов

Автор: [Соколов Дмитрий]
Версия: 2.0
"""

import json
import os
from jsonschema import validate, ValidationError
from jsonschema import Draft7Validator


class TourValidator:
    """
    Валидатор данных туров с использованием JSON Schema.
    
    Обеспечивает проверку корректности данных туров перед 
    сохранением в базу данных. Использует схемы из папки schemes/tour_schemes.
    
    Атрибуты:
        schemes_path (str): Путь к папке с JSON схемами для туров
        
    Методы:
        get_schema: Загружает схему валидации тура из файла
        validate_tour: Выполняет валидацию данных тура
        validate_with_details: Валидация с детализированными ошибками
        
    Примеры:
        >>> validator = TourValidator()
        >>> data = {
        ...     "destination_id": 1,
        ...     "start_date": "2024-12-01",
        ...     "end_date": "2024-12-10"
        ... }
        >>> validator.validate_tour(data, 'add')
    """
    
    def __init__(self):
        """
        Инициализирует валидатор туров.
        
        Устанавливает путь к папке с JSON схемами для туров.
        """
        self.schemes_path = 'schemes/tour_schemes'
    
    def get_schema(self, schema_type: str = 'add') -> dict:
        """
        Загружает JSON схему валидации тура из файла.
        
        Args:
            schema_type (str): Тип схемы ('add' для создания, 'update' для обновления)
            
        Returns:
            dict: Загруженная JSON схема для валидации туров
            
        Raises:
            FileNotFoundError: Если файл схемы не найден
            JSONDecodeError: Если файл содержит некорректный JSON
            
        Пример:
            >>> schema = validator.get_schema('add')
            >>> print(schema['properties']['start_date']['type'])
            'string'
        """
        schema_file = f'{schema_type}_tour.schema.json'
        schema_path = os.path.join(self.schemes_path, schema_file)
        
        with open(schema_path, 'r', encoding='utf-8') as file:
            schema = json.load(file)
        return schema
    
    def validate_tour(self, json_data: dict, schema_type: str = 'add') -> None:
        """
        Валидирует данные тура по выбранной схеме.
        
        Args:
            json_data (dict): Данные тура для валидации
            schema_type (str): Тип схемы ('add' или 'update')
            
        Raises:
            ValidationError: Если данные не соответствуют схеме
            FileNotFoundError: Если файл схемы не найден
            
        Пример:
            >>> data = {
            ...     "destination_id": 1,
            ...     "start_date": "2024-12-01", 
            ...     "end_date": "2024-12-10",
            ...     "available_slots": 20
            ... }
            >>> validator.validate_tour(data, 'add')
        """
        schema = self.get_schema(schema_type)
        validate(instance=json_data, schema=schema)
    
    def validate_with_details(self, json_data: dict, schema_type: str = 'add') -> list:
        """
        Валидирует данные тура и возвращает детализированный список ошибок.
        
        Args:
            json_data (dict): Данные тура для валидации
            schema_type (str): Тип схемы ('add' или 'update')
            
        Returns:
            list: Список объектов ValidationError с деталями ошибок валидации
            
        Пример:
            >>> data = {"destination_id": "invalid", "available_slots": -5}
            >>> errors = validator.validate_with_details(data, 'add')
            >>> for error in errors:
            ...     print(f"Ошибка в поле {error.path}: {error.message}")
        """
        schema = self.get_schema(schema_type)
        validator = Draft7Validator(schema)
        errors = list(validator.iter_errors(json_data))
        return errors