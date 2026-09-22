"""Lead API routes."""
from fastapi import APIRouter, Query, HTTPException, Query as QueryParam
from typing import Optional, List
from app.services.lead_service import LeadService
from app.utils.responses import success_response, error_response

router = APIRouter(prefix="/leads", tags=["Leads"])

# Service instance
lead_service = LeadService()


@router.get("")
async def get_leads(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    assigned_to: Optional[str] = Query(None, alias="assignedTo", description="Filter by assigned BD"),
    product: Optional[str] = Query(None, description="Filter by product"),
    source: Optional[str] = Query(None, description="Filter by source"),
    search: Optional[str] = Query(None, description="Search by name, email, or phone"),
    min_score: Optional[int] = Query(None, alias="minScore", description="Minimum lead score"),
    max_score: Optional[int] = Query(None, alias="maxScore", description="Maximum lead score"),
    sort_by: str = Query("createdAt", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order: asc or desc")
):
    """Get all leads with pagination and filtering."""
    filters = {}
    
    if status:
        # Handle comma-separated status values
        if "," in status:
            filters["status"] = [s.strip() for s in status.split(",")]
        else:
            filters["status"] = status
    
    if priority:
        if "," in priority:
            filters["priority"] = [p.strip() for p in priority.split(",")]
        else:
            filters["priority"] = priority
    
    if assigned_to:
        filters["assignedTo"] = assigned_to
    
    if product:
        filters["product"] = product
    
    if source:
        filters["source"] = source
    
    if search:
        filters["search"] = search
    
    if min_score is not None:
        filters["minScore"] = min_score
    
    if max_score is not None:
        filters["maxScore"] = max_score
    
    result = lead_service.get_all_leads(
        page=page,
        per_page=per_page,
        filters=filters,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    return success_response({
        "leads": result["leads"],
        "pagination": {
            "page": result["page"],
            "perPage": result["perPage"],
            "total": result["total"],
            "totalPages": result["totalPages"]
        }
    }, "Leads fetched successfully")


@router.post("")
async def create_lead(lead_data: dict):
    """Create a new lead."""
    try:
        # Validate required fields
        required_fields = ["name", "email", "product", "budget"]
        for field in required_fields:
            if field not in lead_data:
                return error_response(f"Missing required field: {field}")
        
        lead = lead_service.create_lead(lead_data)
        return success_response(lead, "Lead created successfully")
    except Exception as e:
        return error_response(f"Failed to create lead: {str(e)}")


@router.get("/high-value")
async def get_high_value_leads(limit: int = Query(10, ge=1, le=50)):
    """Get high-value leads."""
    leads = lead_service.get_high_value_leads(limit)
    return success_response(leads, "High-value leads fetched successfully")


@router.get("/statistics")
async def get_lead_statistics():
    """Get lead statistics."""
    stats = lead_service.get_statistics()
    return success_response(stats, "Lead statistics fetched successfully")


@router.get("/{lead_id}")
async def get_lead(lead_id: str):
    """Get a lead by ID."""
    lead = lead_service.get_lead_by_id(lead_id)
    if not lead:
        return error_response("Lead not found")
    return success_response(lead, "Lead fetched successfully")


@router.put("/{lead_id}")
async def update_lead(lead_id: str, update_data: dict):
    """Update a lead."""
    lead = lead_service.update_lead(lead_id, update_data)
    if not lead:
        return error_response("Lead not found or update failed")
    return success_response(lead, "Lead updated successfully")


@router.delete("/{lead_id}")
async def delete_lead(lead_id: str):
    """Delete a lead."""
    success = lead_service.delete_lead(lead_id)
    if not success:
        return error_response("Lead not found or delete failed")
    return success_response({"deleted": True}, "Lead deleted successfully")


@router.post("/{lead_id}/calculate-score")
async def calculate_score(lead_id: str):
    """Calculate and update lead score."""
    result = lead_service.calculate_and_update_score(lead_id)
    if not result:
        return error_response("Lead not found")
    return success_response(result, "Lead score calculated successfully")


@router.get("/{lead_id}/activities")
async def get_lead_activities(lead_id: str, limit: int = Query(50, ge=1, le=200)):
    """Get activities for a lead."""
    from app.services.activity_service import ActivityService
    activity_service = ActivityService()
    
    # Check if lead exists
    lead = lead_service.get_lead_by_id(lead_id)
    if not lead:
        return error_response("Lead not found")
    
    activities = activity_service.get_activities_for_lead(lead_id, limit)
    return success_response(activities["activities"], "Activities fetched successfully")


@router.post("/{lead_id}/activities")
async def create_lead_activity(lead_id: str, activity_data: dict):
    """Create an activity for a lead."""
    from app.services.activity_service import ActivityService
    activity_service = ActivityService()
    
    # Set lead ID
    activity_data["leadId"] = lead_id
    
    try:
        activity = activity_service.create_activity(activity_data)
        return success_response(activity, "Activity created successfully")
    except ValueError as e:
        return error_response(str(e))
    except Exception as e:
        return error_response(f"Failed to create activity: {str(e)}")
