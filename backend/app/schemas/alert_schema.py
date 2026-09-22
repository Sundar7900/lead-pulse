"""Alert schemas for notifications."""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from enum import Enum


class AlertType(str, Enum):
    """Alert type enumeration."""
    HIGH_VALUE_LEAD = "HIGH_VALUE_LEAD"
    FOLLOW_UP_REQUIRED = "FOLLOW_UP_REQUIRED"
    LEAD_INACTIVE = "LEAD_INACTIVE"
    CONVERSION_OPPORTUNITY = "CONVERSION_OPPORTUNITY"
    DEMO_SCHEDULED = "DEMO_SCHEDULED"
    PAYMENT_PENDING = "PAYMENT_PENDING"


class AlertSeverity(str, Enum):
    """Alert severity enumeration."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AlertBase(BaseModel):
    """Base alert schema."""
    type: AlertType
    leadId: str
    leadName: str
    message: str
    severity: AlertSeverity = AlertSeverity.MEDIUM


class AlertCreate(AlertBase):
    """Schema for creating a new alert."""
    pass


class AlertInDB(AlertBase):
    """Alert in database schema."""
    id: str = Field(alias="_id")
    isRead: bool = False
    actionTaken: bool = False
    createdAt: datetime
    readAt: Optional[datetime] = None

    model_config = ConfigDict(populate_by_name=True)


class AlertResponse(BaseModel):
    """Alert response schema."""
    id: str
    type: AlertType
    leadId: str
    leadName: str
    message: str
    severity: AlertSeverity
    isRead: bool
    actionTaken: bool
    createdAt: datetime
    readAt: Optional[datetime] = None


class AlertListResponse(BaseModel):
    """Alert list response."""
    success: bool = True
    data: list
    unreadCount: int
    total: int
    message: str = "Alerts fetched successfully"


class AlertUpdateResponse(BaseModel):
    """Alert update response."""
    success: bool = True
    message: str = "Alert marked as read"
