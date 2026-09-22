"""Alert service for business logic."""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.repositories.alert_repository import AlertRepository
from app.repositories.lead_repository import LeadRepository


# Alert type constants
class AlertTypes:
    HIGH_VALUE_LEAD = "HIGH_VALUE_LEAD"
    FOLLOW_UP_REQUIRED = "FOLLOW_UP_REQUIRED"
    LEAD_INACTIVE = "LEAD_INACTIVE"
    CONVERSION_OPPORTUNITY = "CONVERSION_OPPORTUNITY"
    DEMO_SCHEDULED = "DEMO_SCHEDULED"
    PAYMENT_PENDING = "PAYMENT_PENDING"


class AlertSeverities:
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AlertService:
    """Service for alert business logic."""
    
    def __init__(self):
        self.alert_repo = AlertRepository()
        self.lead_repo = LeadRepository()
    
    def get_all_alerts(
        self,
        page: int = 1,
        per_page: int = 50,
        alert_type: str = None,
        severity: str = None,
        is_read: bool = None,
        lead_id: str = None
    ) -> Dict[str, Any]:
        """Get all alerts with pagination and filtering."""
        skip = (page - 1) * per_page
        
        filters = {}
        if alert_type:
            filters["type"] = alert_type
        if severity:
            filters["severity"] = severity
        if is_read is not None:
            filters["isRead"] = is_read
        if lead_id:
            filters["leadId"] = lead_id
        
        alerts, total = self.alert_repo.find_all(
            skip=skip,
            limit=per_page,
            filters=filters
        )
        
        unread_count = self.alert_repo.count_unread()
        
        return {
            "alerts": [self._format_alert(a) for a in alerts],
            "total": total,
            "unreadCount": unread_count,
            "page": page,
            "perPage": per_page
        }
    
    def get_alert_by_id(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """Get an alert by ID."""
        alert = self.alert_repo.find_by_id(alert_id)
        if alert:
            return self._format_alert(alert)
        return None
    
    def get_unread_alerts(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get all unread alerts."""
        alerts = self.alert_repo.find_unread(limit)
        return [self._format_alert(a) for a in alerts]
    
    def mark_as_read(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """Mark an alert as read."""
        alert = self.alert_repo.mark_as_read(alert_id)
        if alert:
            return self._format_alert(alert)
        return None
    
    def mark_all_read(self, severity: str = None, alert_type: str = None) -> int:
        """Mark multiple alerts as read."""
        filters = {}
        if severity:
            filters["severity"] = severity
        if alert_type:
            filters["type"] = alert_type
        
        return self.alert_repo.mark_all_read(filters)
    
    def create_alert(
        self,
        alert_type: str,
        lead_id: str,
        lead_name: str,
        message: str,
        severity: str = AlertSeverities.MEDIUM
    ) -> Dict[str, Any]:
        """Create a new alert."""
        alert_data = {
            "type": alert_type,
            "leadId": lead_id,
            "leadName": lead_name,
            "message": message,
            "severity": severity
        }
        
        alert = self.alert_repo.create(alert_data)
        return self._format_alert(alert)
    
    def create_high_value_alert(self, lead: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create high-value lead alert if not exists."""
        # Check if alert already exists
        if self.alert_repo.exists_for_lead_type(lead["_id"], AlertTypes.HIGH_VALUE_LEAD):
            return None
        
        return self.create_alert(
            alert_type=AlertTypes.HIGH_VALUE_LEAD,
            lead_id=lead["_id"],
            lead_name=lead["name"],
            message=f"{lead['name']} has been identified as a high-value lead with score {lead.get('leadScore', 0)}.",
            severity=AlertSeverities.HIGH
        )
    
    def create_follow_up_alert(self, lead: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create follow-up required alert."""
        # Check if alert already exists for today
        if self.alert_repo.exists_for_lead_type(lead["_id"], AlertTypes.FOLLOW_UP_REQUIRED):
            return None
        
        return self.create_alert(
            alert_type=AlertTypes.FOLLOW_UP_REQUIRED,
            lead_id=lead["_id"],
            lead_name=lead["name"],
            message=f"Follow-up required for {lead['name']}. Scheduled follow-up was missed.",
            severity=AlertSeverities.MEDIUM
        )
    
    def create_inactive_alert(self, lead: Dict[str, Any], days_inactive: int) -> Optional[Dict[str, Any]]:
        """Create lead inactive alert."""
        if self.alert_repo.exists_for_lead_type(lead["_id"], AlertTypes.LEAD_INACTIVE):
            return None
        
        return self.create_alert(
            alert_type=AlertTypes.LEAD_INACTIVE,
            lead_id=lead["_id"],
            lead_name=lead["name"],
            message=f"{lead['name']} has been inactive for {days_inactive} days.",
            severity=AlertSeverities.LOW
        )
    
    def create_conversion_opportunity_alert(self, lead: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create conversion opportunity alert."""
        if self.alert_repo.exists_for_lead_type(lead["_id"], AlertTypes.CONVERSION_OPPORTUNITY):
            return None
        
        budget_lakhs = lead.get("budget", 0) // 100000
        return self.create_alert(
            alert_type=AlertTypes.CONVERSION_OPPORTUNITY,
            lead_id=lead["_id"],
            lead_name=lead["name"],
            message=f"{lead['name']} shows high conversion potential. Budget: ₹{budget_lakhs}L.",
            severity=AlertSeverities.HIGH
        )
    
    def delete_alert(self, alert_id: str) -> bool:
        """Delete an alert."""
        return self.alert_repo.delete(alert_id)
    
    def delete_alerts_for_lead(self, lead_id: str) -> int:
        """Delete all alerts for a lead."""
        return self.alert_repo.delete_for_lead(lead_id)
    
    def check_and_create_alerts(self) -> List[Dict[str, Any]]:
        """
        Check all leads and create necessary alerts.
        This can be called periodically or on-demand.
        """
        created_alerts = []
        now = datetime.utcnow()
        
        # 1. Check for high-value leads without alerts
        high_value_leads = self.lead_repo.find_high_value(limit=100)
        for lead in high_value_leads:
            if lead.get("status") not in ["converted", "lost"]:
                alert = self.create_high_value_alert(lead)
                if alert:
                    created_alerts.append(alert)
        
        # 2. Check for leads requiring follow-up
        follow_up_leads = self.lead_repo.find_notifications_required()
        for lead in follow_up_leads:
            alert = self.create_follow_up_alert(lead)
            if alert:
                created_alerts.append(alert)
        
        # 3. Check for inactive leads
        all_leads = list(self.lead_repo.find_all(limit=200)[0])
        for lead in all_leads:
            if lead.get("status") not in ["converted", "lost", "new"]:
                last_activity = lead.get("lastActivityAt")
                if last_activity:
                    days_inactive = (now - last_activity.replace(tzinfo=None)).days
                    if days_inactive >= 14:
                        alert = self.create_inactive_alert(lead, days_inactive)
                        if alert:
                            created_alerts.append(alert)
        
        # 4. Check for conversion opportunities
        for lead in all_leads:
            if lead.get("status") == "interested" and lead.get("budget", 0) >= 500000:
                alert = self.create_conversion_opportunity_alert(lead)
                if alert:
                    created_alerts.append(alert)
        
        return created_alerts
    
    def get_summary(self) -> Dict[str, Any]:
        """Get alert summary statistics."""
        return {
            "total": self.alert_repo.collection.count_documents({}),
            "unread": self.alert_repo.count_unread(),
            "byType": self.alert_repo.count_by_type(),
            "bySeverity": self.alert_repo.count_by_severity()
        }
    
    def _format_alert(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        """Format alert for API response."""
        return {
            "id": alert.get("_id"),
            "type": alert.get("type"),
            "leadId": alert.get("leadId"),
            "leadName": alert.get("leadName"),
            "message": alert.get("message"),
            "severity": alert.get("severity"),
            "isRead": alert.get("isRead", False),
            "actionTaken": alert.get("actionTaken", False),
            "createdAt": alert.get("createdAt"),
            "readAt": alert.get("readAt")
        }
