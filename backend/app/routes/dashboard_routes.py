"""Dashboard API routes."""
from fastapi import APIRouter, Query
from app.services.dashboard_service import DashboardService
from app.utils.responses import success_response, error_response

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

dashboard_service = DashboardService()


@router.get("/summary")
async def get_dashboard_summary():
    """Get dashboard summary metrics and highlights."""
    try:
        data = dashboard_service.get_summary()
        return success_response(data, "Dashboard summary fetched successfully")
    except Exception as e:
        return error_response(f"Failed to fetch dashboard summary: {str(e)}")


@router.get("/statistics")
async def get_dashboard_statistics():
    """Get detailed dashboard statistics and breakdowns."""
    try:
        data = dashboard_service.get_statistics()
        return success_response(data, "Dashboard statistics fetched successfully")
    except Exception as e:
        return error_response(f"Failed to fetch dashboard statistics: {str(e)}")


@router.get("/trends")
async def get_dashboard_trends(days: int = Query(30, ge=7, le=90, description="Number of days to analyze")):
    """Get lead creation and activity trends over time."""
    try:
        data = dashboard_service.get_trends(days=days)
        return success_response(data, "Dashboard trends fetched successfully")
    except Exception as e:
        return error_response(f"Failed to fetch dashboard trends: {str(e)}")


@router.get("/bd-performance")
async def get_bd_performance():
    """Get performance metrics for each Business Development representative."""
    try:
        data = dashboard_service.get_bd_performance()
        return success_response(data, "BD performance fetched successfully")
    except Exception as e:
        return error_response(f"Failed to fetch BD performance: {str(e)}")
