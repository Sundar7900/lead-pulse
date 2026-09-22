"""Dashboard service for statistics and analytics."""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from app.repositories.lead_repository import LeadRepository
from app.repositories.alert_repository import AlertRepository
from app.repositories.activity_repository import ActivityRepository


class DashboardService:
    """Service for dashboard statistics and analytics."""
    
    def __init__(self):
        self.lead_repo = LeadRepository()
        self.alert_repo = AlertRepository()
        self.activity_repo = ActivityRepository()
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get dashboard summary with key metrics.
        
        Returns:
            Dictionary with total leads, breakdowns, and highlights
        """
        # Get lead statistics
        lead_stats = self.lead_repo.get_statistics()
        
        # Get alert statistics
        unread_alerts = self.alert_repo.count_unread()
        
        # Calculate averages
        total_leads = lead_stats.get("total", 0)
        total_budget = 0
        total_score = 0
        
        # Get all leads for calculations
        all_leads, _ = self.lead_repo.find_all(limit=1000)
        
        for lead in all_leads:
            total_budget += lead.get("budget", 0)
            total_score += lead.get("leadScore", 0)
        
        avg_score = round(total_score / total_leads, 1) if total_leads > 0 else 0
        avg_budget = int(total_budget / total_leads) if total_leads > 0 else 0
        
        # Get high-value leads
        high_value_leads = self.lead_repo.find_high_value(limit=5)
        
        # Get unread alerts
        recent_alerts = self.alert_repo.find_unread(limit=5)
        
        return {
            "overview": {
                "totalLeads": total_leads,
                "highValueLeads": lead_stats.get("high_value", 0),
                "mediumValueLeads": lead_stats.get("medium_value", 0),
                "lowValueLeads": lead_stats.get("low_value", 0),
                "convertedLeads": lead_stats.get("converted", 0),
                "lostLeads": lead_stats.get("lost", 0),
                "newLeads": lead_stats.get("new", 0),
                "followUpRequired": lead_stats.get("follow_up_required", 0),
                "unreadAlerts": unread_alerts
            },
            "financials": {
                "totalBudget": total_budget,
                "avgBudget": avg_budget,
                "conversionBudget": sum(l.get("budget", 0) for l in all_leads if l.get("status") == "converted")
            },
            "scores": {
                "averageScore": avg_score,
                "highPriority": lead_stats.get("high_value", 0),
                "mediumPriority": lead_stats.get("medium_value", 0),
                "lowPriority": lead_stats.get("low_value", 0)
            },
            "highlights": {
                "highValueLeads": [
                    {
                        "id": l.get("_id"),
                        "name": l.get("name"),
                        "score": l.get("leadScore", 0),
                        "product": l.get("product"),
                        "budget": l.get("budget"),
                        "status": l.get("status")
                    } for l in high_value_leads
                ],
                "recentAlerts": [
                    {
                        "id": a.get("_id"),
                        "type": a.get("type"),
                        "leadName": a.get("leadName"),
                        "message": a.get("message"),
                        "severity": a.get("severity")
                    } for a in recent_alerts
                ]
            }
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get detailed dashboard statistics.
        
        Returns:
            Dictionary with breakdowns by status, priority, and score distribution
        """
        # Get all leads for analysis
        all_leads, total_count = self.lead_repo.find_all(limit=1000)
        
        # Leads by status
        status_counts = self.lead_repo.count_by_status()
        leads_by_status = []
        for status, count in status_counts.items():
            percentage = round((count / total_count) * 100, 1) if total_count > 0 else 0
            leads_by_status.append({
                "status": status,
                "count": count,
                "percentage": percentage
            })
        
        # Leads by priority
        priority_counts = self.lead_repo.count_by_priority()
        leads_by_priority = []
        for priority, count in priority_counts.items():
            percentage = round((count / total_count) * 100, 1) if total_count > 0 else 0
            leads_by_priority.append({
                "priority": priority,
                "count": count,
                "percentage": percentage
            })
        
        # Score distribution
        score_ranges = [
            {"range": "0-19", "min": 0, "max": 19},
            {"range": "20-39", "min": 20, "max": 39},
            {"range": "40-59", "min": 40, "max": 59},
            {"range": "60-79", "min": 60, "max": 79},
            {"range": "80+", "min": 80, "max": 1000},
        ]
        
        score_distribution = []
        for score_range in score_ranges:
            count = len([l for l in all_leads 
                        if score_range["min"] <= l.get("leadScore", 0) <= score_range["max"]])
            percentage = round((count / total_count) * 100, 1) if total_count > 0 else 0
            score_distribution.append({
                "range": score_range["range"],
                "count": count,
                "percentage": percentage
            })
        
        # Leads by product
        product_counts = {}
        for lead in all_leads:
            product = lead.get("product", "Other")
            product_counts[product] = product_counts.get(product, 0) + 1
        
        leads_by_product = [
            {"product": p, "count": c, "percentage": round((c / total_count) * 100, 1)}
            for p, c in sorted(product_counts.items(), key=lambda x: x[1], reverse=True)
        ]
        
        # Leads by source
        source_counts = {}
        for lead in all_leads:
            source = lead.get("source", "Other")
            source_counts[source] = source_counts.get(source, 0) + 1
        
        leads_by_source = [
            {"source": s, "count": c, "percentage": round((c / total_count) * 100, 1)}
            for s, c in sorted(source_counts.items(), key=lambda x: x[1], reverse=True)
        ]
        
        # Leads by assigned BD
        bd_counts = {}
        for lead in all_leads:
            bd_name = lead.get("assignedToName", "Unassigned")
            bd_counts[bd_name] = bd_counts.get(bd_name, 0) + 1
        
        leads_by_bd = [
            {"name": n, "count": c, "percentage": round((c / total_count) * 100, 1)}
            for n, c in sorted(bd_counts.items(), key=lambda x: x[1], reverse=True)
        ]
        
        return {
            "overview": {
                "totalLeads": total_count,
                "totalBudget": sum(l.get("budget", 0) for l in all_leads),
                "averageScore": round(sum(l.get("leadScore", 0) for l in all_leads) / total_count, 1) if total_count > 0 else 0
            },
            "breakdowns": {
                "byStatus": leads_by_status,
                "byPriority": leads_by_priority,
                "byProduct": leads_by_product[:10],  # Top 10
                "bySource": leads_by_source[:10],   # Top 10
                "byBD": leads_by_bd[:10]            # Top 10
            },
            "scoreDistribution": score_distribution,
            "conversionMetrics": {
                "conversionRate": round((status_counts.get("converted", 0) / total_count) * 100, 1) if total_count > 0 else 0,
                "lostRate": round((status_counts.get("lost", 0) / total_count) * 100, 1) if total_count > 0 else 0,
                "pipelineSize": sum(l.get("budget", 0) for l in all_leads if l.get("status") in ["interested", "demo_scheduled", "negotiation"])
            }
        }
    
    def get_trends(self, days: int = 30) -> Dict[str, Any]:
        """
        Get lead trends over time.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dictionary with trend data
        """
        all_leads, _ = self.lead_repo.find_all(limit=1000)
        
        # Group by creation date
        date_counts = {}
        for lead in all_leads:
            created_at = lead.get("createdAt")
            if created_at:
                date_str = created_at.strftime("%Y-%m-%d") if hasattr(created_at, 'strftime') else str(created_at)[:10]
                date_counts[date_str] = date_counts.get(date_str, 0) + 1
        
        # Fill in missing dates
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        trends = []
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            trends.append({
                "date": date_str,
                "leadsCreated": date_counts.get(date_str, 0)
            })
            current_date += timedelta(days=1)
        
        return {
            "period": f"{days} days",
            "trends": trends
        }
    
    def get_bd_performance(self) -> List[Dict[str, Any]]:
        """
        Get performance metrics for each BD.
        
        Returns:
            List of BD performance data
        """
        all_leads, _ = self.lead_repo.find_all(limit=1000)
        
        bd_data = {}
        for lead in all_leads:
            bd_name = lead.get("assignedToName", "Unassigned")
            bd_id = lead.get("assignedTo", "unknown")
            
            if bd_id not in bd_data:
                bd_data[bd_id] = {
                    "id": bd_id,
                    "name": bd_name,
                    "totalLeads": 0,
                    "convertedLeads": 0,
                    "highValueLeads": 0,
                    "totalBudget": 0,
                    "conversionRate": 0,
                    "avgScore": 0,
                    "scores": []
                }
            
            bd_data[bd_id]["totalLeads"] += 1
            bd_data[bd_id]["totalBudget"] += lead.get("budget", 0)
            bd_data[bd_id]["scores"].append(lead.get("leadScore", 0))
            
            if lead.get("status") == "converted":
                bd_data[bd_id]["convertedLeads"] += 1
            
            if lead.get("priority") == "high":
                bd_data[bd_id]["highValueLeads"] += 1
        
        # Calculate rates
        performance = []
        for bd_id, data in bd_data.items():
            data["avgScore"] = round(sum(data["scores"]) / len(data["scores"]), 1) if data["scores"] else 0
            data["conversionRate"] = round((data["convertedLeads"] / data["totalLeads"]) * 100, 1) if data["totalLeads"] > 0 else 0
            del data["scores"]
            performance.append(data)
        
        return sorted(performance, key=lambda x: x["totalLeads"], reverse=True)
