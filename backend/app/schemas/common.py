from pydantic import BaseModel
from typing import Generic, TypeVar, List, Optional
from pydantic import ConfigDict

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    limit: int
