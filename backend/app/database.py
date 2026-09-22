"""Database connection manager with fallback to in-memory storage."""
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from app.config import settings
from app.memory_db import memory_db


class Database:
    """MongoDB database connection manager with in-memory fallback."""
    
    client = None
    db = None
    is_connected: bool = False
    use_memory: bool = False
    
    @classmethod
    def connect(cls):
        """Connect to MongoDB or fallback to in-memory database."""
        try:
            cls.client = MongoClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=2000  # 2 second timeout
            )
            # Test connection
            cls.client.admin.command('ping')
            cls.db = cls.client[settings.DATABASE_NAME]
            cls.is_connected = True
            cls.use_memory = False
            print(f"[OK] Connected to MongoDB: {settings.DATABASE_NAME}")
        except Exception as e:
            cls.is_connected = True  # We're still "connected" to memory
            cls.use_memory = True
            cls.db = memory_db
            print("[INFO] MongoDB not available, using in-memory database")
            print("  Note: Data will not persist. Start MongoDB for persistent storage.")
    
    @classmethod
    def close(cls):
        """Close MongoDB connection."""
        if cls.client and not cls.use_memory:
            cls.client.close()
            print("MongoDB connection closed")
        cls.is_connected = False
    
    @classmethod
    def get_collection(cls, collection_name: str):
        """Get a collection from the database."""
        if not cls.is_connected:
            cls.connect()
        return cls.db.get_collection(collection_name)
    
    @classmethod
    def check_connection(cls) -> bool:
        """Check if database is connected."""
        return cls.is_connected
    
    @classmethod
    def is_memory_db(cls) -> bool:
        """Check if using in-memory database."""
        return cls.use_memory


# Collection names
COLLECTIONS = {
    "leads": "leads",
    "activities": "activities",
    "alerts": "alerts",
    "users": "users"
}


def get_db():
    """Dependency to get database instance."""
    return Database.db
