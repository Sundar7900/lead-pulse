"""Activity schemas for tracking lead interactions."""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum


class ActivityType(str, Enum):
    """Activity type enumeration."""
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    DEMO = "demo"
    PRICING_DISCUSSION = "pricing_discussion"
    FOLLOW_UP = "follow_up"
    PAYMENT = "payment"
    NOTE = "note"
    WHATSAPP = "whatsapp"
    LINKEDIN_MESSAGE = "linkedin_message"


class ActivityOutcome(str, Enum):
    """Activity outcome enumeration."""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    NO_RESPONSE = "no_response"
    FOLLOW_UP_REQUIRED = "follow_up_required"
    SCHEDULED = "scheduled"


class ActivityBase(BaseModel):
    """Base activity schema."""
    type: ActivityType
    description: Optional[str] = None
    outcome: Optional[ActivityOutcome] = None


class ActivityCreate(ActivityBase):
    """Schema for creating a new activity."""
    leadId: str
    nextFollowUpAt: Optional[datetime] = None


class ActivityUpdate(BaseModel):
    """Schema for updating an activity."""
    type: Optional[ActivityType] = None
    description: Optional[str] = None
    outcome: Optional[ActivityOutcome] = None
    nextFollowUpAt: Optional[datetime] = None


class ActivityInDB(ActivityBase):
    """Activity in database schema."""
    id: str = Field(alias="_id")
    leadId: str
    performedBy: Optional[str] = None
    performedByName: Optional[str] = None
    performedAt: datetime
    createdAt: datetime
    nextFollowUpAt: Optional[datetime] = None

    model_config = ConfigDict(populate_by_name=True)


class ActivityResponse(BaseModel):
    """Activity response schema."""
    id: str
    leadId: str
    type: ActivityType
    description: Optional[str] = None
    outcome: Optional[ActivityOutcome] = None
    performedBy: Optional[str] = None
    performedByName: Optional[str] = None
    performedAt: datetime
    nextFollowUpAt: Optional[datetime] = None
    createdAt: datetime


class ActivityListResponse(BaseModel):
    """Activity list response."""
    success: bool = True
    data: list
    total: int
    message: str = "Activities fetched successfully"
