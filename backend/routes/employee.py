from fastapi import APIRouter, Depends, HTTPException, UploadFile, Form, File
from bson import ObjectId
from database import employees_collection, employers_collection, attendance_collection
from auth import get_current_user
from utils import hash_password, get_face_encoding
import numpy as np

router = APIRouter()

# Get employee details route
@router.get("/details")
async def get_employee_details(current_user: dict = Depends(get_current_user)):
    if current_user["type"] != "employee":
        raise HTTPException(status_code=403, detail="Access forbidden")

    try:
        employee_id = ObjectId(current_user["id"])
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid employee ID format")

    employee = await employees_collection.find_one({"_id": employee_id})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    return {
        "username": employee["username"],
        "email": employee["email"],
        "hourly_rate": employee["hourly_rate"],
        "id": str(employee["_id"]),
    }

# Employee registration route
@router.post("/register", status_code=201)
async def register_employee(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    employer_id: str = Form(...),
    hourly_rate: float = Form(...),
    image: UploadFile = File(...)
):
    existing_user = await employees_collection.find_one({"email": email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Employee already exists")

    image_bytes = await image.read()

    try:
        face_encoding = get_face_encoding(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")

    # FACE DUPLICATE CHECK DISABLED (intentionally for now)

    employee_data = {
        "username": username,
        "email": email,
        "password": hash_password(password),
        "face_encoding": face_encoding,
        "employer_id": employer_id,
        "hourly_rate": hourly_rate
    }

    new_employee = await employees_collection.insert_one(employee_data)
    return {"message": "Employee registered successfully", "id": str(new_employee.inserted_id)}

# New route for employee to see attendance summary
@router.get("/attendance/summary")
async def attendance_summary(current_user: dict = Depends(get_current_user)):
    if current_user["type"] != "employee":
        raise HTTPException(status_code=403, detail="Access forbidden")

    employee_id = str(current_user["id"])
    attendance_cursor = attendance_collection.find({"employee_id": employee_id})

    total_hours = 0
    total_earnings = 0
    last_check_in = None
    last_check_out = None
    is_working = False

    async for record in attendance_cursor:
        if record.get("hours_worked"):
            total_hours += record["hours_worked"]
        if record.get("earnings"):
            total_earnings += record["earnings"]
        if record.get("check_in") and not record.get("check_out"):
            is_working = True
            last_check_in = record["check_in"]
        if record.get("check_out"):
            last_check_out = record["check_out"]

    return {
        "total_hours_worked": round(total_hours, 2),
        "total_earnings": round(total_earnings, 2),
        "currently_working": is_working,
        "last_check_in": last_check_in,
        "last_check_out": last_check_out
    }
# ✅ NEW: Get full attendance history for employee
@router.get("/attendance/history")
async def attendance_history(current_user: dict = Depends(get_current_user)):
    if current_user["type"] != "employee":
        raise HTTPException(status_code=403, detail="Access forbidden")

    employee_id = str(current_user["id"])
    cursor = attendance_collection.find({"employee_id": employee_id})
    history = []

    async for record in cursor:
        history.append({
            "check_in": record.get("check_in"),
            "check_out": record.get("check_out"),
            "hours_worked": record.get("hours_worked"),
            "earnings": record.get("earnings")
        })

    return history
