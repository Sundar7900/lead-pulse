"""Lead service for business logic."""
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.repositories.lead_repository import LeadRepository
from app.repositories.activity_repository import ActivityRepository
from app.services.scoring_service import scoring_service
from app.config import settings


class LeadService:
    """Service for lead business logic."""
    
    def __init__(self):
        self.lead_repo = LeadRepository()
        self.activity_repo = ActivityRepository()
    
    def get_all_leads(
        self,
        page: int = 1,
        per_page: int = 20,
        filters: Dict[str, Any] = None,
        sort_by: str = "createdAt",
        sort_order: str = "desc"
    ) -> Dict[str, Any]:
        """Get all leads with pagination."""
        skip = (page - 1) * per_page
        sort_order_int = -1 if sort_order == "desc" else 1
        
        leads, total = self.lead_repo.find_all(
            skip=skip,
            limit=per_page,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order_int
        )
        
        # Format leads for response
        formatted_leads = [self._format_lead(lead) for lead in leads]
        
        return {
            "leads": formatted_leads,
            "total": total,
            "page": page,
            "perPage": per_page,
            "totalPages": (total + per_page - 1) // per_page
        }
    
    def get_lead_by_id(self, lead_id: str) -> Optional[Dict[str, Any]]:
        """Get a lead by ID."""
        lead = self.lead_repo.find_by_id(lead_id)
        if lead:
            return self._format_lead(lead)
        return None
    
    def create_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new lead."""
        # Calculate initial score
        score_result = self.calculate_score_from_data(lead_data)
        
        lead_data["leadScore"] = score_result["totalScore"]
        lead_data["priority"] = score_result["priority"]
        lead_data["scoreBreakdown"] = score_result["scoreBreakdown"]
        
        if "status" not in lead_data:
            lead_data["status"] = "new"
        
        lead = self.lead_repo.create(lead_data)
        return self._format_lead(lead)
    
    def update_lead(self, lead_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a lead."""
        lead = self.lead_repo.update(lead_id, update_data)
        if lead:
            return self._format_lead(lead)
        return None
    
    def delete_lead(self, lead_id: str) -> bool:
        """Delete a lead and its activities."""
        # Delete activities first
        self.activity_repo.delete_by_lead(lead_id)
        return self.lead_repo.delete(lead_id)
    
    def get_high_value_leads(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get high-value leads."""
        leads = self.lead_repo.find_high_value(limit)
        return [self._format_lead(lead) for lead in leads]
    
    def calculate_score_from_data(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate lead score from data using scoring service."""
        return scoring_service.calculate_score(lead_data)
    
    def calculate_and_update_score(self, lead_id: str) -> Optional[Dict[str, Any]]:
        """Calculate score for a lead and update it."""
        lead = self.lead_repo.find_by_id(lead_id)
        if not lead:
            return None
        
        # Get call count
        call_count = self.activity_repo.count_calls_for_lead(lead_id)
        
        # Check recent activity
        last_activity = lead.get("lastActivityAt")
        recent_activity = False
        if last_activity:
            days_since_activity = (datetime.utcnow() - last_activity).days
            recent_activity = days_since_activity <= 7
        
        # Build score data
        score_data = {
            "budget": lead.get("budget", 0),
            "demoRequested": lead.get("demoRequested", False),
            "pricingRequested": lead.get("pricingRequested", False),
            "dpPaid": lead.get("dpPaid", False),
            "callCount": call_count,
            "recentActivity": recent_activity
        }
        
        score_result = self.calculate_score_from_data(score_data)
        
        # Update lead
        updated_lead = self.lead_repo.update_score(
            lead_id,
            score_result["totalScore"],
            score_result["priority"],
            score_result["scoreBreakdown"]
        )
        
        if updated_lead:
            return {
                "lead": self._format_lead(updated_lead),
                "score": score_result
            }
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get lead statistics."""
        return self.lead_repo.get_statistics()
    
    def update_last_activity(self, lead_id: str, activity_time: datetime = None):
        """Update last activity timestamp for a lead."""
        if activity_time is None:
            activity_time = datetime.utcnow()
        
        self.lead_repo.update(lead_id, {
            "lastActivityAt": activity_time
        })
    
    def _format_lead(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """Format lead for API response."""
        return {
            "id": lead.get("_id"),
            "name": lead.get("name"),
            "email": lead.get("email"),
            "phone": lead.get("phone"),
            "location": lead.get("location"),
            "product": lead.get("product"),
            "budget": lead.get("budget"),
            "status": lead.get("status"),
            "priority": lead.get("priority"),
            "leadScore": lead.get("leadScore", 0),
            "source": lead.get("source"),
            "assignedTo": lead.get("assignedTo"),
            "assignedToName": lead.get("assignedToName"),
            "demoRequested": lead.get("demoRequested", False),
            "pricingRequested": lead.get("pricingRequested", False),
            "dpPaid": lead.get("dpPaid", False),
            "lastActivityAt": lead.get("lastActivityAt"),
            "nextFollowUpAt": lead.get("nextFollowUpAt"),
            "createdAt": lead.get("createdAt"),
            "updatedAt": lead.get("updatedAt"),
            "scoreBreakdown": lead.get("scoreBreakdown", [])
        }
