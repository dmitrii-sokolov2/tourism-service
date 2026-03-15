import json
import os
from jsonschema import validate, ValidationError
from jsonschema import Draft7Validator


class UserValidator:
    def __init__(self):
        self.schemes_path = 'schemes/user_schemes'
    
    def get_schema(self, schema_type: str = 'add') -> dict:
        schema_file = f'{schema_type}_user.schema.json'
        schema_path = os.path.join(self.schemes_path, schema_file)
        
        with open(schema_path, 'r', encoding='utf-8') as file:
            schema = json.load(file)
        return schema
    
    def validate_user(self, json_data: dict, schema_type: str = 'add') -> None:
        schema = self.get_schema(schema_type)
        validate(instance=json_data, schema=schema)
    
    def validate_with_details(self, json_data: dict, schema_type: str = 'add') -> list:
        schema = self.get_schema(schema_type)
        validator = Draft7Validator(schema)
        errors = list(validator.iter_errors(json_data))
        return errors