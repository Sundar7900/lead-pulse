"""Alert API routes."""
from fastapi import APIRouter, Query
from typing import Optional
from app.services.alert_service import AlertService
from app.utils.responses import success_response, error_response

router = APIRouter(prefix="/alerts", tags=["Alerts"])

# Service instance
alert_service = AlertService()


@router.get("")
async def get_alerts(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=200, description="Items per page"),
    type: Optional[str] = Query(None, description="Filter by alert type"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    is_read: Optional[bool] = Query(None, alias="isRead", description="Filter by read status"),
    lead_id: Optional[str] = Query(None, alias="leadId", description="Filter by lead ID")
):
    """Get all alerts with pagination and filtering."""
    result = alert_service.get_all_alerts(
        page=page,
        per_page=per_page,
        alert_type=type,
        severity=severity,
        is_read=is_read,
        lead_id=lead_id
    )
    
    return success_response({
        "alerts": result["alerts"],
        "pagination": {
            "page": result["page"],
            "perPage": result["perPage"],
            "total": result["total"]
        },
        "unreadCount": result["unreadCount"]
    }, "Alerts fetched successfully")


@router.get("/unread")
async def get_unread_alerts(limit: int = Query(20, ge=1, le=100)):
    """Get all unread alerts."""
    alerts = alert_service.get_unread_alerts(limit)
    return success_response(alerts, "Unread alerts fetched successfully")


@router.get("/summary")
async def get_alert_summary():
    """Get alert summary statistics."""
    summary = alert_service.get_summary()
    return success_response(summary, "Alert summary fetched successfully")


@router.post("/check")
async def check_and_create_alerts():
    """Check all leads and create necessary alerts."""
    try:
        created = alert_service.check_and_create_alerts()
        return success_response({
            "createdCount": len(created),
            "alerts": created
        }, f"Checked leads and created {len(created)} new alerts")
    except Exception as e:
        return error_response(f"Failed to check alerts: {str(e)}")


@router.get("/{alert_id}")
async def get_alert(alert_id: str):
    """Get an alert by ID."""
    alert = alert_service.get_alert_by_id(alert_id)
    if not alert:
        return error_response("Alert not found")
    return success_response(alert, "Alert fetched successfully")


@router.put("/{alert_id}/read")
async def mark_alert_as_read(alert_id: str):
    """Mark an alert as read."""
    alert = alert_service.mark_as_read(alert_id)
    if not alert:
        return error_response("Alert not found")
    return success_response(alert, "Alert marked as read")


@router.put("/mark-all-read")
async def mark_all_alerts_as_read(
    severity: Optional[str] = Query(None, description="Only mark alerts with this severity"),
    type: Optional[str] = Query(None, description="Only mark alerts with this type")
):
    """Mark multiple alerts as read."""
    count = alert_service.mark_all_read(severity=severity, alert_type=type)
    return success_response({
        "updated": count
    }, f"Marked {count} alerts as read")


@router.delete("/{alert_id}")
async def delete_alert(alert_id: str):
    """Delete an alert."""
    success = alert_service.delete_alert(alert_id)
    if not success:
        return error_response("Alert not found or delete failed")
    return success_response({"deleted": True}, "Alert deleted successfully")
