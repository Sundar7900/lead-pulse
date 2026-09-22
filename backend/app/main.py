"""LeadPulse FastAPI Application."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Database
from app.routes import lead_router, scoring_router, alert_router, dashboard_router

# Import seed function
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from seed.seed_data import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    Database.connect()
    
    # Auto-seed if using in-memory database (for development)
    if Database.is_memory_db():
        print("  Auto-seeding in-memory database...")
        seed_database(use_mongodb=False)
    
    yield
    # Shutdown
    Database.close()


app = FastAPI(
    title="LeadPulse API",
    description="Sales Intelligence Dashboard API - Monitoring leads, calculating scores, and managing alerts",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000,*")
origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(lead_router, prefix="/api")
app.include_router(scoring_router, prefix="/api")
app.include_router(alert_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")


# ============================================
# BASIC ENDPOINTS
# ============================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "success": True,
        "message": "Welcome to LeadPulse API",
        "data": {
            "version": "1.0.0",
            "database": "mongodb" if not Database.is_memory_db() else "in-memory",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/api/status")
async def get_status():
    """Get system status including database connection."""
    try:
        leads_count = Database.get_collection("leads").count_documents({})
        activities_count = Database.get_collection("activities").count_documents({})
        alerts_count = Database.get_collection("alerts").count_documents({})
        users_count = Database.get_collection("users").count_documents({})
    except:
        leads_count = 0
        activities_count = 0
        alerts_count = 0
        users_count = 0
    
    return {
        "success": True,
        "data": {
            "database": {
                "connected": Database.check_connection(),
                "type": "mongodb" if not Database.is_memory_db() else "in-memory",
            },
            "counts": {
                "leads": leads_count,
                "activities": activities_count,
                "alerts": alerts_count,
                "users": users_count
            }
        },
        "message": "System status retrieved successfully"
    }


@app.get("/api/test-db")
async def test_db():
    """Test database connection."""
    try:
        # Try to list collections to verify connection
        db = Database.db
        collections = db.list_collection_names()
        return {
            "success": True,
            "message": "Database connection successful",
            "data": {
                "collections": collections,
                "using_memory": Database.is_memory_db()
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Database connection failed: {str(e)}"
        }


@app.post("/api/seed")
async def seed_db():
    """Seed the database with mock data."""
    try:
        result = seed_database(use_mongodb=not Database.is_memory_db())
        return {
            "success": True,
            "message": "Database seeded successfully",
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Seeding failed: {str(e)}"
        }
