"""
Модуль валидации данных пользователей с использованием JSON Schema.

Содержит класс UserValidator для валидации данных пользователей 
по предопределенным схемам в формате JSON Schema.

Основные возможности:
- Валидация данных при создании пользователя
- Валидация данных при обновлении пользователя  
- Детализированные сообщения об ошибках валидации
- Поддержка различных типов схем (add, update)

Использует:
- jsonschema: Для валидации по JSON Schema стандарту
- Draft7Validator: Для расширенной валидации с детальными ошибками

Автор: [Соколов Дмитрий]
Версия: 2.0
"""

import json
import os
from jsonschema import validate, ValidationError
from jsonschema import Draft7Validator


class UserValidator:
    """
    Валидатор данных пользователей с использованием JSON Schema.
    
    Обеспечивает проверку корректности данных пользователей перед 
    сохранением в базу данных. Использует схемы из папки schemes/user_schemes.
    
    Атрибуты:
        schemes_path (str): Путь к папке с JSON схемами
        
    Методы:
        get_schema: Загружает схему валидации из файла
        validate_user: Выполняет валидацию данных пользователя
        validate_with_details: Валидация с детализированными ошибками
        
    Примеры:
        >>> validator = UserValidator()
        >>> data = {"name": "John", "email": "john@example.com"}
        >>> validator.validate_user(data, 'add')
    """
    
    def __init__(self):
        """
        Инициализирует валидатор пользователей.
        
        Устанавливает путь к папке с JSON схемами для пользователей.
        """
        self.schemes_path = 'schemes/user_schemes'
    
    def get_schema(self, schema_type: str = 'add') -> dict:
        """
        Загружает JSON схему валидации из файла.
        
        Args:
            schema_type (str): Тип схемы ('add' для создания, 'update' для обновления)
            
        Returns:
            dict: Загруженная JSON схема
            
        Raises:
            FileNotFoundError: Если файл схемы не найден
            JSONDecodeError: Если файл содержит некорректный JSON
            
        Пример:
            >>> schema = validator.get_schema('add')
            >>> print(schema['title'])
            'User Creation Schema'
        """
        schema_file = f'{schema_type}_user.schema.json'
        schema_path = os.path.join(self.schemes_path, schema_file)
        
        with open(schema_path, 'r', encoding='utf-8') as file:
            schema = json.load(file)
        return schema
    
    def validate_user(self, json_data: dict, schema_type: str = 'add') -> None:
        """
        Валидирует данные пользователя по выбранной схеме.
        
        Args:
            json_data (dict): Данные пользователя для валидации
            schema_type (str): Тип схемы ('add' или 'update')
            
        Raises:
            ValidationError: Если данные не соответствуют схеме
            FileNotFoundError: Если файл схемы не найден
            
        Пример:
            >>> data = {"name": "John", "email": "john@example.com"}
            >>> validator.validate_user(data, 'add')
            # Если валидация успешна - исключений нет
        """
        schema = self.get_schema(schema_type)
        validate(instance=json_data, schema=schema)
    
    def validate_with_details(self, json_data: dict, schema_type: str = 'add') -> list:
        """
        Валидирует данные и возвращает детализированный список ошибок.
        
        Args:
            json_data (dict): Данные пользователя для валидации
            schema_type (str): Тип схемы ('add' или 'update')
            
        Returns:
            list: Список объектов ValidationError с деталями ошибок
            
        Пример:
            >>> data = {"name": "", "email": "invalid-email"}
            >>> errors = validator.validate_with_details(data, 'add')
            >>> for error in errors:
            ...     print(f"{error.json_path}: {error.message}")
        """
        schema = self.get_schema(schema_type)
        validator = Draft7Validator(schema)
        errors = list(validator.iter_errors(json_data))
        return errors