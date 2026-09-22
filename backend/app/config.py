"""Application configuration."""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings."""
    
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "leadpulse")
    
    # Scoring thresholds
    LOW_SCORE_THRESHOLD: int = 40
    MEDIUM_SCORE_THRESHOLD: int = 70
    
    # Scoring weights
    HIGH_BUDGET_THRESHOLD: int = 500000  # ₹5 Lakh
    HIGH_BUDGET_POINTS: int = 20
    MEDIUM_BUDGET_THRESHOLD: int = 200000  # ₹2 Lakh
    MEDIUM_BUDGET_POINTS: int = 10
    
    DEMO_REQUESTED_POINTS: int = 20
    PRICING_REQUESTED_POINTS: int = 15
    RECENT_ACTIVITY_POINTS: int = 10
    MULTIPLE_CALLS_THRESHOLD: int = 3
    MULTIPLE_CALLS_POINTS: int = 10
    DP_PAID_POINTS: int = 25


settings = Settings()
