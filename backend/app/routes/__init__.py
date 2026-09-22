"""Export all routes."""
from app.routes.lead_routes import router as lead_router
from app.routes.scoring_routes import router as scoring_router
from app.routes.alert_routes import router as alert_router
from app.routes.dashboard_routes import router as dashboard_router

__all__ = [
    "lead_router",
    "scoring_router",
    "alert_router",
    "dashboard_router"
]
