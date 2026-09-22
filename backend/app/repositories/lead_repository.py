"""Lead repository for database operations."""
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.database import Database, COLLECTIONS


class LeadRepository:
    """Repository for lead database operations."""
    
    def __init__(self):
        self.collection = Database.get_collection(COLLECTIONS["leads"])
    
    def find_all(
        self,
        skip: int = 0,
        limit: int = 20,
        filters: Dict[str, Any] = None,
        sort_by: str = "createdAt",
        sort_order: int = -1
    ) -> tuple:
        """
        Find all leads with pagination and filtering.
        
        Returns: (leads_list, total_count)
        """
        filters = filters or {}
        
        # Build query
        query = {}
        
        if filters.get("status"):
            if isinstance(filters["status"], list):
                query["status"] = {"$in": filters["status"]}
            else:
                query["status"] = filters["status"]
        
        if filters.get("priority"):
            if isinstance(filters["priority"], list):
                query["priority"] = {"$in": filters["priority"]}
            else:
                query["priority"] = filters["priority"]
        
        if filters.get("assignedTo"):
            query["assignedTo"] = filters["assignedTo"]
        
        if filters.get("product"):
            query["product"] = filters["product"]
        
        if filters.get("source"):
            query["source"] = filters["source"]
        
        if filters.get("search"):
            # Text search on name and email
            search_regex = {"$regex": filters["search"], "$options": "i"}
            query["$or"] = [
                {"name": search_regex},
                {"email": search_regex},
                {"phone": search_regex}
            ]
        
        # Min score filter
        if filters.get("minScore") is not None:
            query["leadScore"] = {"$gte": filters["minScore"]}
        
        # Max score filter
        if filters.get("maxScore") is not None:
            if "leadScore" in query:
                query["leadScore"]["$lte"] = filters["maxScore"]
            else:
                query["leadScore"] = {"$lte": filters["maxScore"]}
        
        # Get total count
        total = self.collection.count_documents(query)
        
        # Get paginated results
        cursor = self.collection.find(query)
        cursor.skip(skip).limit(limit)
        cursor.sort(sort_by, sort_order)
        
        leads = list(cursor)
        return leads, total
    
    def find_by_id(self, lead_id: str) -> Optional[Dict[str, Any]]:
        """Find a lead by ID."""
        lead = self.collection.find_one({"_id": lead_id})
        return lead
    
    def find_high_value(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Find high-value leads."""
        leads = self.collection.find({"priority": "high"})
        return list(leads.limit(limit).sort("leadScore", -1))
    
    def find_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Find leads by status."""
        leads = self.collection.find({"status": status})
        return list(leads)
    
    def find_notifications_required(self) -> List[Dict[str, Any]]:
        """Find leads that need follow-up notifications."""
        now = datetime.utcnow()
        leads = self.collection.find({
            "nextFollowUpAt": {"$lt": now},
            "status": {"$nin": ["converted", "lost"]}
        })
        return list(leads)
    
    def create(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new lead."""
        now = datetime.utcnow()
        lead_data["createdAt"] = now
        lead_data["updatedAt"] = now
        
        if "status" not in lead_data:
            lead_data["status"] = "new"
        if "priority" not in lead_data:
            lead_data["priority"] = "low"
        if "leadScore" not in lead_data:
            lead_data["leadScore"] = 0
        if "scoreBreakdown" not in lead_data:
            lead_data["scoreBreakdown"] = []
        
        result = self.collection.insert_one(lead_data)
        lead_data["_id"] = result.inserted_id
        return lead_data
    
    def update(self, lead_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a lead."""
        update_data["updatedAt"] = datetime.utcnow()
        
        result = self.collection.update_one(
            {"_id": lead_id},
            {"$set": update_data}
        )
        
        if result.matched_count > 0:
            return self.find_by_id(lead_id)
        return None
    
    def update_score(
        self, 
        lead_id: str, 
        score: int, 
        priority: str, 
        breakdown: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Update lead score and priority."""
        update_data = {
            "leadScore": score,
            "priority": priority,
            "scoreBreakdown": breakdown,
            "updatedAt": datetime.utcnow()
        }
        
        result = self.collection.update_one(
            {"_id": lead_id},
            {"$set": update_data}
        )
        
        if result.matched_count > 0:
            return self.find_by_id(lead_id)
        return None
    
    def delete(self, lead_id: str) -> bool:
        """Delete a lead."""
        result = self.collection.delete_one({"_id": lead_id})
        return result.deleted_count > 0
    
    def count_by_status(self) -> Dict[str, int]:
        """Count leads by status."""
        pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        results = list(self.collection.aggregate(pipeline))
        return {r["_id"]: r["count"] for r in results}
    
    def count_by_priority(self) -> Dict[str, int]:
        """Count leads by priority."""
        pipeline = [
            {"$group": {"_id": "$priority", "count": {"$sum": 1}}}
        ]
        results = list(self.collection.aggregate(pipeline))
        return {r["_id"]: r["count"] for r in results}
    
    def count_all(self) -> int:
        """Count all leads."""
        return self.collection.count_documents({})
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get lead statistics."""
        total = self.count_all()
        
        by_status = self.count_by_status()
        by_priority = self.count_by_priority()
        
        # Calculate totals
        high_value = by_priority.get("high", 0)
        medium_value = by_priority.get("medium", 0)
        low_value = by_priority.get("low", 0)
        
        converted = by_status.get("converted", 0)
        lost = by_status.get("lost", 0)
        new = by_status.get("new", 0)
        
        # Follow-up required
        follow_up_count = len(self.find_notifications_required())
        
        return {
            "total": total,
            "by_status": by_status,
            "by_priority": by_priority,
            "high_value": high_value,
            "medium_value": medium_value,
            "low_value": low_value,
            "converted": converted,
            "lost": lost,
            "new": new,
            "follow_up_required": follow_up_count
        }
