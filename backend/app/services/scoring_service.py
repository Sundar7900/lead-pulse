"""
Lead Scoring Service

This service calculates lead scores based on configurable rules.
The scoring engine evaluates multiple factors and produces:
- Total score (0-100+)
- Priority level (high/medium/low)
- Score breakdown with reasons

Scoring Factors:
1. Budget - Higher budget = higher score
2. Engagement - Demo/Pricing requests
3. Commitment - Down payment
4. Activity - Call count, recent activity
5. Status - Current lead status
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from app.config import settings


class ScoringRule:
    """Base class for scoring rules."""
    
    def __init__(self, name: str, points: int, description: str):
        self.name = name
        self.points = points
        self.description = description
    
    def evaluate(self, lead_data: Dict[str, Any]) -> tuple[bool, int, str]:
        """
        Evaluate the rule against lead data.
        
        Returns: (passed, points, reason)
        """
        raise NotImplementedError


class BudgetRule(ScoringRule):
    """Score based on budget amount."""
    
    def __init__(self):
        super().__init__(
            name="budget",
            points=0,  # Determined dynamically
            description="Budget-based scoring"
        )
    
    def evaluate(self, lead_data: Dict[str, Any]) -> tuple[bool, int, str]:
        budget = lead_data.get("budget", 0)
        
        if budget >= settings.HIGH_BUDGET_THRESHOLD:
            budget_lakhs = budget // 100000
            return (True, settings.HIGH_BUDGET_POINTS, f"High budget (₹{budget_lakhs}L+)")
        
        elif budget >= settings.MEDIUM_BUDGET_THRESHOLD:
            budget_lakhs = budget // 100000
            return (True, settings.MEDIUM_BUDGET_POINTS, f"Medium budget (₹{budget_lakhs}L)")
        
        return (False, 0, "Budget below threshold")


class DemoRequestedRule(ScoringRule):
    """Score if demo has been requested."""
    
    def __init__(self):
        super().__init__(
            name="demo_requested",
            points=settings.DEMO_REQUESTED_POINTS,
            description="Demo requested"
        )
    
    def evaluate(self, lead_data: Dict[str, Any]) -> tuple[bool, int, str]:
        if lead_data.get("demoRequested", False):
            return (True, self.points, "Demo requested")
        return (False, 0, "No demo requested")


class PricingRequestedRule(ScoringRule):
    """Score if pricing has been requested."""
    
    def __init__(self):
        super().__init__(
            name="pricing_requested",
            points=settings.PRICING_REQUESTED_POINTS,
            description="Pricing discussion requested"
        )
    
    def evaluate(self, lead_data: Dict[str, Any]) -> tuple[bool, int, str]:
        if lead_data.get("pricingRequested", False):
            return (True, self.points, "Pricing requested")
        return (False, 0, "No pricing requested")


class DownPaymentRule(ScoringRule):
    """Score if down payment has been made."""
    
    def __init__(self):
        super().__init__(
            name="dp_paid",
            points=settings.DP_PAID_POINTS,
            description="Down payment made"
        )
    
    def evaluate(self, lead_data: Dict[str, Any]) -> tuple[bool, int, str]:
        if lead_data.get("dpPaid", False):
            return (True, self.points, "Down payment made")
        return (False, 0, "No down payment")


class MultipleCallsRule(ScoringRule):
    """Score based on number of calls."""
    
    def __init__(self):
        super().__init__(
            name="multiple_calls",
            points=settings.MULTIPLE_CALLS_POINTS,
            description="Multiple engagement calls"
        )
    
    def evaluate(self, lead_data: Dict[str, Any]) -> tuple[bool, int, str]:
        call_count = lead_data.get("callCount", 0)
        
        if call_count >= settings.MULTIPLE_CALLS_THRESHOLD:
            return (True, self.points, f"Multiple calls ({call_count})")
        
        return (False, 0, f"Few calls ({call_count})")


class RecentActivityRule(ScoringRule):
    """Score if there's recent activity."""
    
    def __init__(self):
        super().__init__(
            name="recent_activity",
            points=settings.RECENT_ACTIVITY_POINTS,
            description="Recent activity (within 7 days)"
        )
    
    def evaluate(self, lead_data: Dict[str, Any]) -> tuple[bool, int, str]:
        last_activity = lead_data.get("lastActivityAt")
        
        if last_activity:
            if isinstance(last_activity, str):
                last_activity = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
            
            days_since = (datetime.utcnow() - last_activity.replace(tzinfo=None)).days
            
            if days_since <= 7:
                return (True, self.points, f"Recent activity ({days_since}d ago)")
        
        # Check if explicitly marked as recent
        if lead_data.get("recentActivity", False):
            return (True, self.points, "Recent activity")
        
        return (False, 0, "No recent activity")


class StatusProgressionRule(ScoringRule):
    """Bonus points for advanced lead status."""
    
    def __init__(self):
        super().__init__(
            name="status_progression",
            points=0,
            description="Status-based bonus"
        )
    
    def evaluate(self, lead_data: Dict[str, Any]) -> tuple[bool, int, str]:
        status = lead_data.get("status", "new")
        
        status_points = {
            "negotiation": 15,
            "demo_scheduled": 10,
            "interested": 5,
            "contacted": 2,
            "new": 0
        }
        
        points = status_points.get(status, 0)
        
        if points > 0:
            return (True, points, f"Status: {status}")
        
        return (False, 0, f"Status: {status}")


class ScoringService:
    """
    Service for calculating lead scores.
    
    The scoring engine applies multiple rules to evaluate a lead's
    potential value. Each rule can add points to the total score.
    
    Priority Levels:
    - HIGH: score >= 70
    - MEDIUM: score >= 40
    - LOW: score < 40
    """
    
    def __init__(self):
        """Initialize scoring rules."""
        self.rules: List[ScoringRule] = [
            BudgetRule(),
            DemoRequestedRule(),
            PricingRequestedRule(),
            DownPaymentRule(),
            MultipleCallsRule(),
            RecentActivityRule(),
            StatusProgressionRule(),
        ]
    
    def calculate_score(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate lead score based on all rules.
        
        Args:
            lead_data: Dictionary containing lead information
            
        Returns:
            Dictionary with totalScore, priority, and scoreBreakdown
        """
        total_score = 0
        score_breakdown = []
        
        for rule in self.rules:
            passed, points, reason = rule.evaluate(lead_data)
            
            if passed and points > 0:
                total_score += points
                score_breakdown.append({
                    "reason": reason,
                    "points": points
                })
        
        # Determine priority
        priority = self._determine_priority(total_score)
        
        return {
            "totalScore": total_score,
            "priority": priority,
            "scoreBreakdown": score_breakdown,
            "thresholds": {
                "high": settings.MEDIUM_SCORE_THRESHOLD,  # >= 70
                "medium": settings.LOW_SCORE_THRESHOLD,   # >= 40
                "low": 0                                 # < 40
            }
        }
    
    def _determine_priority(self, score: int) -> str:
        """Determine priority level based on score."""
        if score >= settings.MEDIUM_SCORE_THRESHOLD:  # >= 70
            return "high"
        elif score >= settings.LOW_SCORE_THRESHOLD:   # >= 40
            return "medium"
        else:
            return "low"
    
    def get_priority_for_score(self, score: int) -> str:
        """Get priority level for a given score."""
        return self._determine_priority(score)
    
    def get_scoring_factors(self) -> List[Dict[str, Any]]:
        """
        Get list of all scoring factors with their configurations.
        
        Useful for displaying scoring rules to users.
        """
        return [
            {
                "name": "Budget",
                "highThreshold": f"₹{settings.HIGH_BUDGET_THRESHOLD // 100000}L+",
                "highPoints": settings.HIGH_BUDGET_POINTS,
                "mediumThreshold": f"₹{settings.MEDIUM_BUDGET_THRESHOLD // 100000}L-₹{settings.HIGH_BUDGET_THRESHOLD // 100000}L",
                "mediumPoints": settings.MEDIUM_BUDGET_POINTS
            },
            {
                "name": "Demo Requested",
                "points": settings.DEMO_REQUESTED_POINTS,
                "condition": "Lead has requested product demo"
            },
            {
                "name": "Pricing Requested",
                "points": settings.PRICING_REQUESTED_POINTS,
                "condition": "Lead has asked about pricing"
            },
            {
                "name": "Down Payment",
                "points": settings.DP_PAID_POINTS,
                "condition": "Lead has made down payment"
            },
            {
                "name": "Multiple Calls",
                "points": settings.MULTIPLE_CALLS_POINTS,
                "condition": f"≥{settings.MULTIPLE_CALLS_THRESHOLD} calls made"
            },
            {
                "name": "Recent Activity",
                "points": settings.RECENT_ACTIVITY_POINTS,
                "condition": "Activity within last 7 days"
            }
        ]
    
    def get_thresholds(self) -> Dict[str, int]:
        """Get current scoring thresholds."""
        return {
            "high": settings.MEDIUM_SCORE_THRESHOLD,
            "medium": settings.LOW_SCORE_THRESHOLD,
            "low": 0
        }
    
    def batch_calculate(self, leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculate scores for multiple leads.
        
        Args:
            leads: List of lead dictionaries
            
        Returns:
            List of scoring results
        """
        results = []
        for lead in leads:
            result = self.calculate_score(lead)
            result["leadId"] = lead.get("_id") or lead.get("id")
            result["leadName"] = lead.get("name")
            results.append(result)
        return results
    
    def compare_scores(self, lead1: Dict[str, Any], lead2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare scores between two leads.
        
        Returns which lead has higher potential and why.
        """
        score1 = self.calculate_score(lead1)
        score2 = self.calculate_score(lead2)
        
        return {
            "lead1": {
                "id": lead1.get("_id") or lead1.get("id"),
                "name": lead1.get("name"),
                "score": score1["totalScore"],
                "priority": score1["priority"]
            },
            "lead2": {
                "id": lead2.get("_id") or lead2.get("id"),
                "name": lead2.get("name"),
                "score": score2["totalScore"],
                "priority": score2["priority"]
            },
            "higherPotential": "lead1" if score1["totalScore"] >= score2["totalScore"] else "lead2",
            "scoreDifference": abs(score1["totalScore"] - score2["totalScore"])
        }


# Singleton instance
scoring_service = ScoringService()
