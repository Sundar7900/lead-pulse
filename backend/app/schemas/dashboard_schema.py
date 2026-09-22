"""Dashboard schemas for statistics."""
from pydantic import BaseModel
from typing import List, Dict, Any


class DashboardSummaryResponse(BaseModel):
    """Dashboard summary response."""
    success: bool = True
    data: Dict[str, Any]
    message: str = "Dashboard summary fetched successfully"


class LeadsByPriority(BaseModel):
    """Leads by priority breakdown."""
    priority: str
    count: int
    percentage: float


class LeadsByStatus(BaseModel):
    """Leads by status breakdown."""
    status: str
    count: int
    percentage: float


class ScoreDistribution(BaseModel):
    """Score distribution range."""
    range: str
    count: int


class DashboardStatistics(BaseModel):
    """Dashboard statistics."""
    totalLeads: int
    highValueLeads: int
    mediumValueLeads: int
    lowValueLeads: int
    convertedLeads: int
    lostLeads: int
    followUpRequired: int
    newLeads: int
    unreadAlerts: int
    totalBudget: int
    averageScore: float


class LeadTrend(BaseModel):
    """Lead trend data."""
    date: str
    count: int


class DashboardChartData(BaseModel):
    """Dashboard chart data."""
    leadsByPriority: List[LeadsByPriority]
    leadsByStatus: List[LeadsByStatus]
    scoreDistribution: List[ScoreDistribution]
    leadTrend: List[LeadTrend]


class DashboardStatisticsResponse(BaseModel):
    """Dashboard statistics response."""
    success: bool = True
    data: DashboardStatistics
    message: str = "Dashboard statistics fetched successfully"
