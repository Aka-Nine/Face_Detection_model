from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn
import os

from database import create_indexes
from routes.employee import router as employee_router
from routes.employer import router as employer_router
from routes.attandance import router as attendance_router
from auth import (
    login_with_password,
    login_with_face,
    login_employer_with_face,
    login_employee_with_face
)

# Load environment variables
load_dotenv()

# Validate MongoDB URI
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("❌ MONGO_URI is not set in .env file!")

app = FastAPI(
    title="Attendance Management System",
    version="1.0",
    description="API for managing employee attendance with face recognition and password-based login."
)

# CORS
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/")
async def root():
    return {"message": "Welcome to the Attendance Management System API 🚀"}

# Authentication Routes
app.post("/login/password")(login_with_password)
app.post("/login/face")(login_with_face)
app.post("/login/face/employer")(login_employer_with_face)
app.post("/login/face/employee")(login_employee_with_face)

# Feature Routers
app.include_router(employer_router, prefix="/employer", tags=["Employer"])
app.include_router(employee_router, prefix="/employee", tags=["Employee"])
app.include_router(attendance_router, prefix="/attendance", tags=["Attendance"])

# Startup Events
@app.on_event("startup")
async def startup_db():
    try:
        await create_indexes()
        print("✅ MongoDB indexes created successfully")
    except Exception as e:
        print(f"❌ Error creating indexes: {e}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
