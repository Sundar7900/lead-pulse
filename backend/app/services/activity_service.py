"""Activity service for business logic."""
from typing import Dict, Any, List
from datetime import datetime
from app.repositories.activity_repository import ActivityRepository
from app.repositories.lead_repository import LeadRepository


class ActivityService:
    """Service for activity business logic."""
    
    def __init__(self):
        self.activity_repo = ActivityRepository()
        self.lead_repo = LeadRepository()
    
    def get_activities_for_lead(self, lead_id: str, limit: int = 50) -> Dict[str, Any]:
        """Get all activities for a lead."""
        activities = self.activity_repo.find_by_lead(lead_id, limit)
        formatted = [self._format_activity(a) for a in activities]
        
        return {
            "activities": formatted,
            "total": len(formatted)
        }
    
    def create_activity(self, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new activity."""
        lead_id = activity_data.get("leadId")
        
        # Verify lead exists
        lead = self.lead_repo.find_by_id(lead_id)
        if not lead:
            raise ValueError(f"Lead not found: {lead_id}")
        
        # Get performer info from lead if not provided
        if "performedBy" not in activity_data:
            activity_data["performedBy"] = lead.get("assignedTo")
        if "performedByName" not in activity_data:
            activity_data["performedByName"] = lead.get("assignedToName")
        
        activity = self.activity_repo.create(activity_data)
        
        # Update lead's last activity time
        self.lead_repo.update(lead_id, {
            "lastActivityAt": activity.get("performedAt"),
            "status": self._determine_status_from_activity(activity, lead)
        })
        
        # Handle next follow-up
        if activity_data.get("nextFollowUpAt"):
            self.lead_repo.update(lead_id, {
                "nextFollowUpAt": activity_data.get("nextFollowUpAt")
            })
        
        return self._format_activity(activity)
    
    def _determine_status_from_activity(
        self, 
        activity: Dict[str, Any], 
        current_lead: Dict[str, Any]
    ) -> str:
        """Determine lead status based on activity."""
        current_status = current_lead.get("status", "new")
        activity_type = activity.get("type")
        outcome = activity.get("outcome")
        
        # Don't change status if already converted or lost
        if current_status in ["converted", "lost"]:
            return current_status
        
        # Status progression logic
        if activity_type == "demo":
            if current_status in ["new", "contacted", "interested"]:
                return "demo_scheduled"
        
        if activity_type == "pricing_discussion":
            if current_status in ["interested", "demo_scheduled"]:
                return "negotiation"
        
        if activity_type == "payment":
            return "converted"
        
        if outcome == "negative" and current_status not in ["demo_scheduled", "negotiation"]:
            return "lost"
        
        # Default progression
        if current_status == "new":
            return "contacted"
        elif current_status == "contacted":
            if activity_type in ["call", "email", "meeting"]:
                return "interested"
        
        return current_status
    
    def _format_activity(self, activity: Dict[str, Any]) -> Dict[str, Any]:
        """Format activity for API response."""
        return {
            "id": activity.get("_id"),
            "leadId": activity.get("leadId"),
            "type": activity.get("type"),
            "description": activity.get("description"),
            "outcome": activity.get("outcome"),
            "performedBy": activity.get("performedBy"),
            "performedByName": activity.get("performedByName"),
            "performedAt": activity.get("performedAt"),
            "nextFollowUpAt": activity.get("nextFollowUpAt"),
            "createdAt": activity.get("createdAt")
        }
