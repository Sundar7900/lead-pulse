"""API Response utilities."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class SuccessResponse(BaseModel):
    """Standard success response."""
    success: bool = True
    data: Any
    message: str = "Success"


class ErrorResponse(BaseModel):
    """Standard error response."""
    success: bool = False
    message: str
    error: Optional[str] = None


class PaginatedResponse(BaseModel):
    """Paginated response."""
    success: bool = True
    data: List[Any]
    total: int
    page: int
    perPage: int
    message: str = "Success"


def success_response(data: Any, message: str = "Success") -> Dict[str, Any]:
    """Create a success response."""
    return {
        "success": True,
        "data": data,
        "message": message
    }


def error_response(message: str, error: str = None) -> Dict[str, Any]:
    """Create an error response."""
    return {
        "success": False,
        "message": message,
        "error": error
    }


def paginated_response(data: List[Any], total: int, page: int, perPage: int, message: str = "Success") -> Dict[str, Any]:
    """Create a paginated response."""
    return {
        "success": True,
        "data": data,
        "total": total,
        "page": page,
        "perPage": perPage,
        "message": message
    }
