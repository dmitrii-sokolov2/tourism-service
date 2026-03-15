from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional


@dataclass
class ProblemDetails:
    type: str = None
    title: str = None  
    status: int = None
    detail: str = None
    instance: str = None
    errors: Optional[List[Dict[str, Any]]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)