"""Activity repository for database operations."""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.database import Database, COLLECTIONS


class ActivityRepository:
    """Repository for activity database operations."""
    
    def __init__(self):
        self.collection = Database.get_collection(COLLECTIONS["activities"])
    
    def find_by_lead(
        self, 
        lead_id: str, 
        limit: int = 50,
        sort_order: int = -1
    ) -> List[Dict[str, Any]]:
        """Find all activities for a lead."""
        activities = self.collection.find({"leadId": lead_id})
        return list(activities.sort("performedAt", sort_order).limit(limit))
    
    def find_by_id(self, activity_id: str) -> Optional[Dict[str, Any]]:
        """Find an activity by ID."""
        return self.collection.find_one({"_id": activity_id})
    
    def create(self, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new activity."""
        now = datetime.utcnow()
        activity_data["createdAt"] = now
        
        if "performedAt" not in activity_data:
            activity_data["performedAt"] = now
        
        result = self.collection.insert_one(activity_data)
        activity_data["_id"] = result.inserted_id
        return activity_data
    
    def count_for_lead(self, lead_id: str) -> int:
        """Count activities for a lead."""
        return self.collection.count_documents({"leadId": lead_id})
    
    def count_calls_for_lead(self, lead_id: str) -> int:
        """Count call activities for a lead."""
        return self.collection.count_documents({
            "leadId": lead_id,
            "type": "call"
        })
    
    def get_recent_activity_types(self, lead_id: str, days: int = 7) -> List[str]:
        """Get recent activity types for a lead."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        activities = self.collection.find({
            "leadId": lead_id,
            "performedAt": {"$gte": cutoff}
        })
        return list(set(a["type"] for a in activities))
    
    def delete_by_lead(self, lead_id: str) -> int:
        """Delete all activities for a lead."""
        result = self.collection.delete_many({"leadId": lead_id})
        return result.deleted_count

