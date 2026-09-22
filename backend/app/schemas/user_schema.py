"""User schemas for BD team members."""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration."""
    ADMIN = "admin"
    SALES_REP = "sales_rep"
    MANAGER = "manager"


class UserBase(BaseModel):
    """Base user schema."""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    role: UserRole = UserRole.SALES_REP
    region: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user."""
    pass


class UserInDB(UserBase):
    """User in database schema."""
    id: str = Field(alias="_id")
    active: bool = True
    createdAt: datetime
    updatedAt: datetime

    model_config = ConfigDict(populate_by_name=True)


class UserResponse(BaseModel):
    """User response schema."""
    id: str
    name: str
    email: str
    role: UserRole
    region: Optional[str] = None
    active: bool


class UserListResponse(BaseModel):
    """User list response."""
    success: bool = True
    data: list
    total: int
    message: str = "Users fetched successfully"
