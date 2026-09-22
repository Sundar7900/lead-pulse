"""Scoring API routes."""
from fastapi import APIRouter, HTTPException
from app.services.scoring_service import scoring_service
from app.utils.responses import success_response, error_response

router = APIRouter(prefix="/scoring", tags=["Scoring"])


@router.get("/factors")
async def get_scoring_factors():
    """Get all scoring factors and their point values."""
    factors = scoring_service.get_scoring_factors()
    return success_response(factors, "Scoring factors retrieved")


@router.get("/thresholds")
async def get_scoring_thresholds():
    """Get current priority thresholds."""
    thresholds = scoring_service.get_thresholds()
    return success_response({
        "thresholds": thresholds,
        "description": {
            "high": f"Score >= {thresholds['high']} = High Priority",
            "medium": f"Score >= {thresholds['medium']} = Medium Priority",
            "low": f"Score < {thresholds['medium']} = Low Priority"
        }
    }, "Scoring thresholds retrieved")


@router.post("/calculate")
async def calculate_score_for_data(lead_data: dict):
    """
    Calculate score for provided lead data.
    
    This endpoint allows testing scoring without updating a lead.
    
    Required fields:
    - budget: int (in rupees)
    
    Optional fields:
    - demoRequested: bool
    - pricingRequested: bool
    - dpPaid: bool
    - callCount: int
    - recentActivity: bool
    - lastActivityAt: datetime
    - status: str
    """
    try:
        result = scoring_service.calculate_score(lead_data)
        return success_response(result, "Score calculated successfully")
    except Exception as e:
        return error_response(f"Failed to calculate score: {str(e)}")


@router.post("/batch")
async def batch_calculate_scores(leads: list):
    """
    Calculate scores for multiple leads.
    
    Body: Array of lead objects
    """
    try:
        results = scoring_service.batch_calculate(leads)
        return success_response(results, f"Calculated scores for {len(results)} leads")
    except Exception as e:
        return error_response(f"Batch calculation failed: {str(e)}")


@router.post("/compare")
async def compare_lead_scores(leads: list):
    """
    Compare scores between two leads.
    
    Body: Array with exactly 2 lead objects
    """
    try:
        if len(leads) != 2:
            return error_response("Exactly 2 leads required for comparison")
        
        result = scoring_service.compare_scores(leads[0], leads[1])
        return success_response(result, "Leads compared successfully")
    except Exception as e:
        return error_response(f"Comparison failed: {str(e)}")
