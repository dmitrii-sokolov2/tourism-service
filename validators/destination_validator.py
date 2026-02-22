"""
Модуль валидации данных направлений с использованием JSON Schema.

Содержит класс DestinationValidator для валидации данных направлений
по предопределенным схемам в формате JSON Schema.

Основные возможности:
- Валидация данных при создании направления
- Валидация данных при обновлении направления
- Проверка уникальности названий в пределах страны
- Валидация числовых значений (цена, продолжительность)
- Детализированные сообщения об ошибках валидации

Особенности валидации направлений:
- Проверка обязательных полей (name, country)
- Валидация price (неотрицательные значения)
- Проверка duration_days (положительные значения)
- Валидация форматов строковых данных

Автор: [Соколов Дмитрий]
Версия: 2.0
"""

import json
import os
from jsonschema import validate, ValidationError
from jsonschema import Draft7Validator


class DestinationValidator:
    """
    Валидатор данных направлений с использованием JSON Schema.
    
    Обеспечивает проверку корректности данных направлений перед 
    сохранением в базу данных. Использует схемы из папки schemes/destination_schemes.
    
    Атрибуты:
        schemes_path (str): Путь к папке с JSON схемами для направлений
        
    Методы:
        get_schema: Загружает схему валидации направления из файла
        validate_destination: Выполняет валидацию данных направления
        validate_with_details: Валидация с детализированными ошибками
        
    Примеры:
        >>> validator = DestinationValidator()
        >>> data = {
        ...     "name": "Париж",
        ...     "country": "Франция", 
        ...     "price": 1200,
        ...     "duration_days": 7
        ... }
        >>> validator.validate_destination(data, 'add')
    """
    
    def __init__(self):
        """
        Инициализирует валидатор направлений.
        
        Устанавливает путь к папке с JSON схемами для направлений.
        """
        self.schemes_path = 'schemes/destination_schemes'
    
    def get_schema(self, schema_type: str = 'add') -> dict:
        """
        Загружает JSON схему валидации направления из файла.
        
        Args:
            schema_type (str): Тип схемы ('add' для создания, 'update' для обновления)
            
        Returns:
            dict: Загруженная JSON схема для валидации направлений
            
        Raises:
            FileNotFoundError: Если файл схемы не найден
            JSONDecodeError: Если файл содержит некорректный JSON
            
        Пример:
            >>> schema = validator.get_schema('add')
            >>> print(schema['required'])
            ['name', 'country', 'price', 'duration_days']
        """
        schema_file = f'{schema_type}_destination.schema.json'
        schema_path = os.path.join(self.schemes_path, schema_file)
        
        with open(schema_path, 'r', encoding='utf-8') as file:
            schema = json.load(file)
        return schema
    
    def validate_destination(self, json_data: dict, schema_type: str = 'add') -> None:
        """
        Валидирует данные направления по выбранной схеме.
        
        Args:
            json_data (dict): Данные направления для валидации
            schema_type (str): Тип схемы ('add' или 'update')
            
        Raises:
            ValidationError: Если данные не соответствуют схеме
            FileNotFoundError: Если файл схемы не найден
            
        Пример:
            >>> data = {
            ...     "name": "Париж",
            ...     "country": "Франция",
            ...     "price": 1200,
            ...     "duration_days": 7
            ... }
            >>> validator.validate_destination(data, 'add')
        """
        schema = self.get_schema(schema_type)
        validate(instance=json_data, schema=schema)
    
    def validate_with_details(self, json_data: dict, schema_type: str = 'add') -> list:
        """
        Валидирует данные направления и возвращает детализированный список ошибок.
        
        Args:
            json_data (dict): Данные направления для валидации
            schema_type (str): Тип схемы ('add' или 'update')
            
        Returns:
            list: Список объектов ValidationError с деталями ошибок валидации
            
        Пример:
            >>> data = {"name": "", "price": -100, "duration_days": 0}
            >>> errors = validator.validate_with_details(data, 'add')
            >>> for error in errors:
            ...     print(f"Ошибка: {error.message} в поле {list(error.path)}")
        """
        schema = self.get_schema(schema_type)
        validator = Draft7Validator(schema)
        errors = list(validator.iter_errors(json_data))
        return errors