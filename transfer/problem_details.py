"""
Модуль для стандартизированного формата ошибок Problem Details.

Содержит класс ProblemDetails для представления ошибок в соответствии 
со стандартом RFC 7807 (Problem Details for HTTP APIs).

Классы:
    ProblemDetails: Dataclass для структурированного описания ошибок

Атрибуты ProblemDetails:
    type (str): URI идентификатор типа ошибки
    title (str): Краткое описание ошибки
    status (int): HTTP статус код
    detail (str): Детальное описание ошибки  
    instance (str): URI конкретного экземпляра ошибки
    errors (list): Дополнительные ошибки валидации

Использование:
    problem = ProblemDetails(
        type="validation_error",
        title="Invalid input",
        status=400,
        detail="The request contains invalid data",
        errors=[{"field": "email", "message": "Invalid email format"}]
    )
    
Автор: [Соколов Дмитрий]
Версия: 1.0
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional


@dataclass
class ProblemDetails:
    """
    Dataclass для представления ошибок в формате Problem Details (RFC 7807).
    
    Обеспечивает стандартизированный формат ответов об ошибках для REST API.
    
    Атрибуты:
        type (str): URI идентификатор типа ошибки (опционально)
        title (str): Краткое человеко-читаемое описание ошибки (опционально)
        status (int): HTTP статус код (опционально)
        detail (str): Детальное человеко-читаемое описание (опционально)
        instance (str): URI конкретного экземпляра ошибки (опционально)
        errors (List[Dict[str, Any]]): Дополнительные ошибки валидации (опционально)
    
    Примеры:
        >>> error = ProblemDetails(
        ...     status=400,
        ...     title="Invalid input",
        ...     detail="Email format is invalid"
        ... )
        >>> error.to_dict()
        {'status': 400, 'title': 'Invalid input', 'detail': 'Email format is invalid'}
    """
    
    type: str = None
    title: str = None  
    status: int = None
    detail: str = None
    instance: str = None
    errors: Optional[List[Dict[str, Any]]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Конвертирует объект ProblemDetails в словарь.
        
        Returns:
            Dict[str, Any]: Словарь с данными ошибки в формате Problem Details
            
        Пример:
            >>> problem = ProblemDetails(title="Error", status=400)
            >>> problem.to_dict()
            {'title': 'Error', 'status': 400}
        """
        return asdict(self)