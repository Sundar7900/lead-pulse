"""Lead schemas for API request/response."""
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


class LeadStatus(str, Enum):
    """Lead status enumeration."""
    NEW = "new"
    CONTACTED = "contacted"
    INTERESTED = "interested"
    DEMO_SCHEDULED = "demo_scheduled"
    NEGOTIATION = "negotiation"
    CONVERTED = "converted"
    LOST = "lost"


class LeadPriority(str, Enum):
    """Lead priority enumeration."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class LeadSource(str, Enum):
    """Lead source enumeration."""
    WEBSITE = "website"
    REFERRAL = "referral"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    GOOGLE_ADS = "google_ads"
    DIRECT = "direct"
    WEBINAR = "webinar"
    COLD_OUTREACH = "cold_outreach"


# Score Breakdown Schema
class ScoreBreakdown(BaseModel):
    """Score breakdown item."""
    reason: str
    points: int


# Lead Schemas
class LeadBase(BaseModel):
    """Base lead schema."""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    location: Optional[str] = Field(None, max_length=100)
    product: str = Field(..., min_length=1, max_length=100)
    budget: int = Field(..., ge=0)
    source: LeadSource = LeadSource.WEBSITE
    assignedTo: Optional[str] = None


class LeadCreate(LeadBase):
    """Schema for creating a new lead."""
    demoRequested: bool = False
    pricingRequested: bool = False
    notes: Optional[str] = None


class LeadUpdate(BaseModel):
    """Schema for updating a lead."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    location: Optional[str] = Field(None, max_length=100)
    product: Optional[str] = Field(None, min_length=1, max_length=100)
    budget: Optional[int] = Field(None, ge=0)
    status: Optional[LeadStatus] = None
    source: Optional[LeadSource] = None
    assignedTo: Optional[str] = None
    demoRequested: Optional[bool] = None
    pricingRequested: Optional[bool] = None
    dpPaid: Optional[bool] = None
    notes: Optional[str] = None
    nextFollowUpAt: Optional[datetime] = None


class LeadInDB(LeadBase):
    """Lead in database schema."""
    id: str = Field(alias="_id")
    status: LeadStatus = LeadStatus.NEW
    priority: LeadPriority = LeadPriority.LOW
    leadScore: int = 0
    demoRequested: bool = False
    pricingRequested: bool = False
    dpPaid: bool = False
    lastActivityAt: Optional[datetime] = None
    nextFollowUpAt: Optional[datetime] = None
    createdAt: datetime
    updatedAt: datetime
    scoreBreakdown: List[ScoreBreakdown] = []

    model_config = ConfigDict(populate_by_name=True)


class LeadResponse(BaseModel):
    """Lead response schema."""
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    product: str
    budget: int
    status: LeadStatus
    priority: LeadPriority
    leadScore: int
    source: LeadSource
    assignedTo: Optional[str] = None
    assignedToName: Optional[str] = None
    demoRequested: bool = False
    pricingRequested: bool = False
    dpPaid: bool = False
    lastActivityAt: Optional[datetime] = None
    nextFollowUpAt: Optional[datetime] = None
    createdAt: datetime
    updatedAt: datetime
    scoreBreakdown: List[ScoreBreakdown] = []


class LeadListResponse(BaseModel):
    """Lead list response with pagination."""
    success: bool = True
    data: List[LeadResponse]
    total: int
    page: int
    perPage: int
    message: str = "Leads fetched successfully"


class LeadScoreResponse(BaseModel):
    """Lead score calculation response."""
    success: bool = True
    data: dict
    message: str = "Lead score calculated successfully"
