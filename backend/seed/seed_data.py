"""Seed data for LeadPulse.

This script populates the database with realistic mock data for:
- Users (Sales Reps/BDs)
- Leads (50-100 sample leads)
- Activities (Call, Email, Demo, etc.)
- Alerts (High-value, Follow-up, etc.)
"""
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.memory_db import InMemoryDB, InMemoryCollection
from app.database import Database
from app.config import settings


# ============================================
# SAMPLE DATA DEFINITIONS
# ============================================

# Users (Sales Reps/BDs)
USERS = [
    {"id": "user_001", "name": "Priya Sharma", "email": "priya@leadpulse.com", "region": "North"},
    {"id": "user_002", "name": "Rahul Verma", "email": "rahul@leadpulse.com", "region": "South"},
    {"id": "user_003", "name": "Ananya Iyer", "email": "ananya@leadpulse.com", "region": "West"},
    {"id": "user_004", "name": "Vikram Patel", "email": "vikram@leadpulse.com", "region": "East"},
    {"id": "user_005", "name": "Sneha Reddy", "email": "sneha@leadpulse.com", "region": "Central"},
]

# Products/Courses
PRODUCTS = [
    "Data Science",
    "Full Stack Development",
    "Cloud Computing",
    "Machine Learning",
    "Cybersecurity",
    "DevOps Engineering",
    "Business Analytics",
    "Artificial Intelligence",
]

# Locations
LOCATIONS = [
    "Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad",
    "Pune", "Kolkata", "Ahmedabad", "Jaipur", "Lucknow",
    "Chandigarh", "Kochi", "Indore", "Nagpur", "Surat",
]

# Lead Sources
SOURCES = [
    "website", "referral", "linkedin", "facebook", "instagram",
    "google_ads", "direct", "webinar", "cold_outreach"
]

# First names and last names for lead generation
FIRST_NAMES = [
    "Arun", "Deepa", "Suresh", "Kavitha", "Ramesh", "Lakshmi", "Manoj", "Saritha",
    "Kumar", "Priya", "Sanjay", "Meena", "Vijay", "Shanti", "Prasad", "Renuka",
    "Anil", "Poornima", "Naveen", "Arundhati", "Ganesh", "Padma", "Shiva", "Geetha",
    "Raju", "Sunitha", "Krishna", "Madhavi", "Nagaraj", "Swathi", "Mahesh", "Kalyani",
    "Harish", "Bhagya", "Rakshith", "Jyothi", "Tanuja", "Rohan", "Asha",
]

LAST_NAMES = [
    "Kumar", "Sharma", "Verma", "Reddy", "Nair", "Iyer", "Patel", "Singh",
    "Rao", "Gupta", "Naidu", "Choudhury", "Desai", "Joshi", "Mehra", "Pillai",
    "Menon", "Hegde", "Bhat", "Kulkarni", "Shetty", "Naik", "Kamat", "D'souza",
]

# Status weights for distribution
STATUSES = [
    ("new", 0.15),
    ("contacted", 0.20),
    ("interested", 0.25),
    ("demo_scheduled", 0.12),
    ("negotiation", 0.10),
    ("converted", 0.10),
    ("lost", 0.08),
]


def get_random_status() -> str:
    """Get a random status based on weights."""
    r = random.random()
    cumulative = 0
    for status, weight in STATUSES:
        cumulative += weight
        if r <= cumulative:
            return status
    return "new"


def get_random_phone() -> str:
    """Generate a random Indian phone number."""
    return f"9{random.randint(100000000, 999999999)}"


def get_random_email(name: str) -> str:
    """Generate a random email based on name."""
    name_parts = name.lower().replace(".", "").split()
    domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "company.com"]
    return f"{''.join(name_parts[:2])}_{random.randint(1, 999)}@{random.choice(domains)}"


def get_random_budget(status: str) -> int:
    """Get a budget based on lead status (higher budget leads more likely to convert)."""
    if status in ["converted", "negotiation"]:
        # Higher budgets for advanced stages
        return random.choice([
            random.randint(400000, 600000),
            random.randint(600000, 800000),
            random.randint(800000, 1200000),
        ])
    elif status in ["demo_scheduled", "interested"]:
        return random.choice([
            random.randint(200000, 400000),
            random.randint(400000, 700000),
            random.randint(700000, 1000000),
        ])
    else:
        return random.choice([
            random.randint(100000, 200000),
            random.randint(200000, 400000),
            random.randint(400000, 800000),
        ])


def calculate_lead_score(budget: int, demo_requested: bool, pricing_requested: bool,
                         dp_paid: bool, recent_activity: bool, call_count: int) -> tuple:
    """Calculate lead score and return (score, priority, breakdown)."""
    score = 0
    breakdown = []

    # Budget scoring
    if budget >= 500000:
        score += 20
        breakdown.append({"reason": "High budget (₹5L+)", "points": 20})
    elif budget >= 200000:
        score += 10
        breakdown.append({"reason": "Medium budget (₹2L-5L)", "points": 10})

    # Demo requested
    if demo_requested:
        score += 20
        breakdown.append({"reason": "Demo requested", "points": 20})

    # Pricing requested
    if pricing_requested:
        score += 15
        breakdown.append({"reason": "Pricing requested", "points": 15})

    # DP paid
    if dp_paid:
        score += 25
        breakdown.append({"reason": "Down payment made", "points": 25})

    # Multiple calls
    if call_count >= 3:
        score += 10
        breakdown.append({"reason": f"Multiple calls ({call_count})", "points": 10})

    # Recent activity
    if recent_activity:
        score += 10
        breakdown.append({"reason": "Recent activity", "points": 10})

    # Determine priority
    if score >= 70:
        priority = "high"
    elif score >= 40:
        priority = "medium"
    else:
        priority = "low"

    return score, priority, breakdown


def generate_leads(count: int = 75) -> List[Dict[str, Any]]:
    """Generate sample leads."""
    leads = []
    used_names = set()

    for i in range(count):
        # Generate unique name
        while True:
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            name = f"{first_name} {last_name}"
            email = get_random_email(name)
            if name not in used_names:
                used_names.add(name)
                break

        # Assign random attributes
        status = get_random_status()
        user = random.choice(USERS)
        budget = get_random_budget(status)

        # Boolean flags based on status
        if status in ["converted", "negotiation"]:
            demo_requested = True
            pricing_requested = random.choice([True, True, False])
            dp_paid = status == "converted"
        elif status == "demo_scheduled":
            demo_requested = True
            pricing_requested = random.choice([True, False])
            dp_paid = False
        elif status == "interested":
            demo_requested = random.choice([True, True, False])
            pricing_requested = random.choice([True, False])
            dp_paid = False
        else:
            demo_requested = random.choice([True, False, False, False])
            pricing_requested = random.choice([True, False, False, False])
            dp_paid = False

        # Activity timestamps
        days_ago = random.randint(1, 60)
        created_at = datetime.utcnow() - timedelta(days=days_ago)

        # Recent activity means within last 7 days
        recent_activity = days_ago <= 7

        # Random call count
        if status in ["converted", "demo_scheduled"]:
            call_count = random.randint(2, 6)
        elif status in ["negotiation", "interested"]:
            call_count = random.randint(1, 4)
        else:
            call_count = random.randint(0, 2)

        # Calculate score
        score, priority, breakdown = calculate_lead_score(
            budget, demo_requested, pricing_requested, dp_paid, recent_activity, call_count
        )

        # Last activity
        if status == "converted":
            last_activity_at = datetime.utcnow() - timedelta(days=random.randint(1, 5))
        elif recent_activity:
            last_activity_at = datetime.utcnow() - timedelta(days=random.randint(0, 7))
        else:
            last_activity_at = datetime.utcnow() - timedelta(days=random.randint(8, 30))

        # Next follow-up
        if status in ["converted", "lost"]:
            next_follow_up = None
        else:
            next_follow_up = datetime.utcnow() + timedelta(days=random.randint(-5, 14))

        lead = {
            "_id": f"lead_{i+1:03d}",
            "name": name,
            "email": email,
            "phone": get_random_phone(),
            "location": random.choice(LOCATIONS),
            "product": random.choice(PRODUCTS),
            "budget": budget,
            "status": status,
            "priority": priority,
            "leadScore": score,
            "source": random.choice(SOURCES),
            "assignedTo": user["id"],
            "assignedToName": user["name"],
            "demoRequested": demo_requested,
            "pricingRequested": pricing_requested,
            "dpPaid": dp_paid,
            "lastActivityAt": last_activity_at,
            "nextFollowUpAt": next_follow_up,
            "createdAt": created_at,
            "updatedAt": created_at,
            "scoreBreakdown": breakdown,
        }
        leads.append(lead)

    return leads


def generate_activities(leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate activities for leads."""
    activities = []
    activity_types = [
        ("call", 0.30),
        ("email", 0.25),
        ("demo", 0.10),
        ("pricing_discussion", 0.08),
        ("follow_up", 0.15),
        ("whatsapp", 0.07),
        ("note", 0.05),
    ]

    outcomes = ["positive", "neutral", "negative", "no_response", "follow_up_required", "scheduled"]

    activity_id = 1

    for lead in leads:
        # Skip converted/lost leads that don't have much history
        if lead["status"] in ["new"]:
            num_activities = random.randint(0, 2)
        elif lead["status"] in ["converted", "lost"]:
            num_activities = random.randint(3, 8)
        else:
            num_activities = random.randint(2, 6)

        base_time = lead["createdAt"]
        current_time = base_time

        for _ in range(num_activities):
            # Random activity type based on weights
            r = random.random()
            cumulative = 0
            activity_type = "call"
            for atype, weight in activity_types:
                cumulative += weight
                if r <= cumulative:
                    activity_type = atype
                    break

            # Adjust current_time (activities happen over time)
            current_time = current_time + timedelta(hours=random.randint(4, 48))
            if current_time > datetime.utcnow():
                current_time = datetime.utcnow() - timedelta(hours=random.randint(1, 24))

            activity = {
                "_id": f"activity_{activity_id:03d}",
                "leadId": lead["_id"],
                "type": activity_type,
                "description": f"{activity_type.replace('_', ' ').title()} with {lead['name']}",
                "outcome": random.choice(outcomes),
                "performedBy": lead["assignedTo"],
                "performedByName": lead.get("assignedToName", "System"),
                "performedAt": current_time,
                "createdAt": current_time,
                "nextFollowUpAt": None,
            }

            # Set next follow-up for some activities
            if activity["outcome"] == "follow_up_required" and lead["status"] not in ["converted", "lost"]:
                activity["nextFollowUpAt"] = current_time + timedelta(days=random.randint(1, 7))

            activities.append(activity)
            activity_id += 1

    return activities


def generate_alerts(leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate alerts based on lead data."""
    alerts = []
    alert_id = 1

    for lead in leads:
        # High-value lead alert
        if lead["priority"] == "high" and lead["status"] not in ["converted", "lost"]:
            alert = {
                "_id": f"alert_{alert_id:03d}",
                "type": "HIGH_VALUE_LEAD",
                "leadId": lead["_id"],
                "leadName": lead["name"],
                "message": f"{lead['name']} has been identified as a high-value lead with score {lead['leadScore']}.",
                "severity": "high",
                "isRead": random.choice([True, False]),
                "actionTaken": False,
                "createdAt": lead["updatedAt"] + timedelta(hours=random.randint(1, 24)),
                "readAt": None,
            }
            alerts.append(alert)
            alert_id += 1

        # Follow-up required alert
        if lead.get("nextFollowUpAt") and lead["nextFollowUpAt"] < datetime.utcnow():
            if lead["status"] not in ["converted", "lost"]:
                alert = {
                    "_id": f"alert_{alert_id:03d}",
                    "type": "FOLLOW_UP_REQUIRED",
                    "leadId": lead["_id"],
                    "leadName": lead["name"],
                    "message": f"Follow-up required for {lead['name']}. Scheduled follow-up was missed.",
                    "severity": "medium",
                    "isRead": False,
                    "actionTaken": False,
                    "createdAt": datetime.utcnow() - timedelta(hours=random.randint(1, 48)),
                    "readAt": None,
                }
                alerts.append(alert)
                alert_id += 1

        # Conversion opportunity alert (interested + high budget)
        if lead["status"] == "interested" and lead["budget"] >= 500000:
            alert = {
                "_id": f"alert_{alert_id:03d}",
                "type": "CONVERSION_OPPORTUNITY",
                "leadId": lead["_id"],
                "leadName": lead["name"],
                "message": f"{lead['name']} shows high conversion potential. Budget: ₹{lead['budget']:,}.",
                "severity": "high",
                "isRead": random.choice([True, False]),
                "actionTaken": False,
                "createdAt": datetime.utcnow() - timedelta(hours=random.randint(1, 72)),
                "readAt": None,
            }
            alerts.append(alert)
            alert_id += 1

        # Lead inactive alert
        if lead["lastActivityAt"] and lead["lastActivityAt"] < datetime.utcnow() - timedelta(days=14):
            if lead["status"] in ["interested", "demo_scheduled", "negotiation"]:
                alert = {
                    "_id": f"alert_{alert_id:03d}",
                    "type": "LEAD_INACTIVE",
                    "leadId": lead["_id"],
                    "leadName": lead["name"],
                    "message": f"{lead['name']} has been inactive for {14 + random.randint(1, 30)} days.",
                    "severity": "low",
                    "isRead": False,
                    "actionTaken": False,
                    "createdAt": datetime.utcnow() - timedelta(hours=random.randint(1, 24)),
                    "readAt": None,
                }
                alerts.append(alert)
                alert_id += 1

    return alerts


def generate_users() -> List[Dict[str, Any]]:
    """Generate user documents."""
    users = []
    for i, user in enumerate(USERS):
        users.append({
            "_id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": "sales_rep",
            "region": user["region"],
            "active": True,
            "createdAt": datetime.utcnow() - timedelta(days=365),
            "updatedAt": datetime.utcnow() - timedelta(days=30),
        })
    return users


# ============================================
# SEED FUNCTION
# ============================================

def seed_database(use_mongodb: bool = True):
    """Seed the database with mock data."""
    print("=" * 50)
    print("LeadPulse - Seeding Database")
    print("=" * 50)

    # Generate data
    print("\n1. Generating users...")
    users = generate_users()
    print(f"   [OK] Generated {len(users)} users")

    print("\n2. Generating leads...")
    leads = generate_leads(75)
    print(f"   [OK] Generated {len(leads)} leads")

    # Statistics
    high_value = sum(1 for l in leads if l["priority"] == "high")
    medium_value = sum(1 for l in leads if l["priority"] == "medium")
    low_value = sum(1 for l in leads if l["priority"] == "low")
    converted = sum(1 for l in leads if l["status"] == "converted")
    lost = sum(1 for l in leads if l["status"] == "lost")
    new = sum(1 for l in leads if l["status"] == "new")
    print(f"   - High-value: {high_value}, Medium: {medium_value}, Low: {low_value}")
    print(f"   - Converted: {converted}, Lost: {lost}, New: {new}")

    print("\n3. Generating activities...")
    activities = generate_activities(leads)
    print(f"   [OK] Generated {len(activities)} activities")

    print("\n4. Generating alerts...")
    alerts = generate_alerts(leads)
    print(f"   [OK] Generated {len(alerts)} alerts")

    # Insert into database
    if use_mongodb and Database.db is not None and not Database.is_memory_db():
        print("\n5. Inserting into MongoDB...")
        
        # Clear existing data
        Database.db.leads.delete_many({})
        Database.db.activities.delete_many({})
        Database.db.alerts.delete_many({})
        Database.db.users.delete_many({})
        
        # Insert new data
        Database.db.users.insert_many(users)
        Database.db.leads.insert_many(leads)
        Database.db.activities.insert_many(activities)
        Database.db.alerts.insert_many(alerts)

        print("   [OK] All data inserted into MongoDB")
    else:
        print("\n5. Inserting into in-memory database...")
        
        # Get collections from in-memory database
        users_coll = Database.db.get_collection("users")
        leads_coll = Database.db.get_collection("leads")
        activities_coll = Database.db.get_collection("activities")
        alerts_coll = Database.db.get_collection("alerts")

        # Clear and insert
        users_coll._data.clear()
        leads_coll._data.clear()
        activities_coll._data.clear()
        alerts_coll._data.clear()

        for user in users:
            users_coll._data.append(user)
        for lead in leads:
            leads_coll._data.append(lead)
        for activity in activities:
            activities_coll._data.append(activity)
        for alert in alerts:
            alerts_coll._data.append(alert)

        print("   [OK] All data inserted into in-memory database")

    print("\n" + "=" * 50)
    print("Database seeding complete!")
    print("=" * 50)
    
    return {
        "users": len(users),
        "leads": len(leads),
        "activities": len(activities),
        "alerts": len(alerts),
    }


if __name__ == "__main__":
    # Run seed script
    from app.database import Database
    
    Database.connect()
    result = seed_database(use_mongodb=not Database.is_memory_db())
    print(f"\nSeeded: {result}")
