"""Alert repository for database operations."""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.database import Database, COLLECTIONS


class AlertRepository:
    """Repository for alert database operations."""
    
    def __init__(self):
        self.collection = Database.get_collection(COLLECTIONS["alerts"])
    
    def find_all(
        self,
        skip: int = 0,
        limit: int = 50,
        filters: Dict[str, Any] = None,
        sort_order: int = -1
    ) -> tuple:
        """
        Find all alerts with pagination and filtering.
        
        Returns: (alerts_list, total_count)
        """
        filters = filters or {}
        query = {}
        
        if filters.get("type"):
            query["type"] = filters["type"]
        
        if filters.get("severity"):
            query["severity"] = filters["severity"]
        
        if filters.get("isRead") is not None:
            query["isRead"] = filters["isRead"]
        
        if filters.get("leadId"):
            query["leadId"] = filters["leadId"]
        
        # Get total count
        total = self.collection.count_documents(query)
        
        # Get paginated results
        alerts = self.collection.find(query)
        alerts.skip(skip).limit(limit)
        alerts.sort("createdAt", sort_order)
        
        return list(alerts), total
    
    def find_by_id(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """Find an alert by ID."""
        return self.collection.find_one({"_id": alert_id})
    
    def find_unread(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Find all unread alerts."""
        alerts = self.collection.find({"isRead": False})
        return list(alerts.sort("createdAt", -1).limit(limit))
    
    def count_unread(self) -> int:
        """Count unread alerts."""
        return self.collection.count_documents({"isRead": False})
    
    def count_by_type(self) -> Dict[str, int]:
        """Count alerts by type."""
        pipeline = [
            {"$group": {"_id": "$type", "count": {"$sum": 1}}}
        ]
        results = list(self.collection.aggregate(pipeline))
        return {r["_id"]: r["count"] for r in results}
    
    def count_by_severity(self) -> Dict[str, int]:
        """Count alerts by severity."""
        pipeline = [
            {"$group": {"_id": "$severity", "count": {"$sum": 1}}}
        ]
        results = list(self.collection.aggregate(pipeline))
        return {r["_id"]: r["count"] for r in results}
    
    def create(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new alert."""
        now = datetime.utcnow()
        alert_data["createdAt"] = now
        alert_data["isRead"] = False
        alert_data["readAt"] = None
        
        if "actionTaken" not in alert_data:
            alert_data["actionTaken"] = False
        
        result = self.collection.insert_one(alert_data)
        alert_data["_id"] = result.inserted_id
        return alert_data
    
    def mark_as_read(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """Mark an alert as read."""
        result = self.collection.update_one(
            {"_id": alert_id},
            {"$set": {
                "isRead": True,
                "readAt": datetime.utcnow()
            }}
        )
        
        if result.matched_count > 0:
            return self.find_by_id(alert_id)
        return None
    
    def mark_all_read(self, filters: Dict[str, Any] = None) -> int:
        """Mark multiple alerts as read."""
        query = {"isRead": False}
        
        if filters:
            if filters.get("severity"):
                query["severity"] = filters["severity"]
            if filters.get("type"):
                query["type"] = filters["type"]
        
        result = self.collection.update_many(
            query,
            {"$set": {
                "isRead": True,
                "readAt": datetime.utcnow()
            }}
        )
        
        return result.modified_count
    
    def delete(self, alert_id: str) -> bool:
        """Delete an alert."""
        result = self.collection.delete_one({"_id": alert_id})
        return result.deleted_count > 0
    
    def delete_for_lead(self, lead_id: str) -> int:
        """Delete all alerts for a lead."""
        result = self.collection.delete_many({"leadId": lead_id})
        return result.deleted_count
    
    def exists_for_lead_type(self, lead_id: str, alert_type: str) -> bool:
        """Check if an alert of this type exists for the lead."""
        count = self.collection.count_documents({
            "leadId": lead_id,
            "type": alert_type
        })
        return count > 0
    
    def get_recent(self, days: int = 7, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent alerts within specified days."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        alerts = self.collection.find({
            "createdAt": {"$gte": cutoff}
        })
        return list(alerts.sort("createdAt", -1).limit(limit))

