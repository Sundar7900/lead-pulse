"""Export all schemas."""
from app.schemas.lead_schema import (
    LeadStatus,
    LeadPriority,
    LeadSource,
    ScoreBreakdown,
    LeadBase,
    LeadCreate,
    LeadUpdate,
    LeadInDB,
    LeadResponse,
    LeadListResponse,
    LeadScoreResponse
)
from app.schemas.activity_schema import (
    ActivityType,
    ActivityOutcome,
    ActivityBase,
    ActivityCreate,
    ActivityUpdate,
    ActivityInDB,
    ActivityResponse,
    ActivityListResponse
)
from app.schemas.alert_schema import (
    AlertType,
    AlertSeverity,
    AlertBase,
    AlertCreate,
    AlertInDB,
    AlertResponse,
    AlertListResponse,
    AlertUpdateResponse
)
from app.schemas.dashboard_schema import (
    DashboardSummaryResponse,
    LeadsByPriority,
    LeadsByStatus,
    ScoreDistribution,
    DashboardStatistics,
    DashboardStatisticsResponse,
    DashboardChartData,
    LeadTrend
)
from app.schemas.user_schema import (
    UserRole,
    UserBase,
    UserCreate,
    UserInDB,
    UserResponse,
    UserListResponse
)

__all__ = [
    # Lead schemas
    "LeadStatus",
    "LeadPriority",
    "LeadSource",
    "ScoreBreakdown",
    "LeadBase",
    "LeadCreate",
    "LeadUpdate",
    "LeadInDB",
    "LeadResponse",
    "LeadListResponse",
    "LeadScoreResponse",
    # Activity schemas
    "ActivityType",
    "ActivityOutcome",
    "ActivityBase",
    "ActivityCreate",
    "ActivityUpdate",
    "ActivityInDB",
    "ActivityResponse",
    "ActivityListResponse",
    # Alert schemas
    "AlertType",
    "AlertSeverity",
    "AlertBase",
    "AlertCreate",
    "AlertInDB",
    "AlertResponse",
    "AlertListResponse",
    "AlertUpdateResponse",
    # Dashboard schemas
    "DashboardSummaryResponse",
    "LeadsByPriority",
    "LeadsByStatus",
    "ScoreDistribution",
    "DashboardStatistics",
    "DashboardStatisticsResponse",
    "DashboardChartData",
    "LeadTrend",
    # User schemas
    "UserRole",
    "UserBase",
    "UserCreate",
    "UserInDB",
    "UserResponse",
    "UserListResponse"
]
