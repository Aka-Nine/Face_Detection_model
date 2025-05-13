from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "attendance_system")

# Enforce TLS 1.2+ using MongoDB Atlas defaults
client = AsyncIOMotorClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=False)

database = client[DATABASE_NAME]
employers_collection = database["employers"]
employees_collection = database["employees"]
attendance_collection = database["attendance"]

async def create_indexes():
    """Create necessary indexes for collections."""
    try:
        await employers_collection.create_index("email", unique=True)
        await employees_collection.create_index("email", unique=True)
        await attendance_collection.create_index("employee_id")
        print("✅ Indexes created successfully!")
    except Exception as e:
        print(f"❌ Failed to create indexes: {e}")

def get_database():
    return database
