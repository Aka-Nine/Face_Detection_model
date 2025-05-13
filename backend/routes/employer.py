from fastapi import APIRouter, HTTPException, UploadFile, Form, File, Depends, Header
from database import employers_collection, employees_collection, attendance_collection
from utils import hash_password, get_face_encoding, compare_faces
from auth import get_current_user
from bson import ObjectId
import numpy as np

router = APIRouter()

# --------------------
# POST /register
# --------------------
@router.post("/register", status_code=201)
async def register_employer(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    image: UploadFile = File(...)
):
    existing_user = await employers_collection.find_one({"email": email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Employer already exists")

    image_bytes = await image.read()
    try:
        face_encoding = get_face_encoding(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")

    for collection in [employers_collection, employees_collection]:
        async for user in collection.find({"face_encoding": {"$exists": True}}):
            stored_encoding = user.get("face_encoding")
            if stored_encoding and compare_faces([np.array(stored_encoding)], face_encoding):
                raise HTTPException(status_code=400, detail="Face already registered")

    employer_data = {
        "username": username,
        "email": email,
        "password": hash_password(password),
        "face_encoding": face_encoding,
    }

    new_employer = await employers_collection.insert_one(employer_data)
    return {"message": "Employer registered successfully", "id": str(new_employer.inserted_id)}

# --------------------
# GET /details
# --------------------
@router.get("/details")
async def get_employer_details(current_user: dict = Depends(get_current_user)):
    if current_user["type"] != "employer":
        raise HTTPException(status_code=403, detail="Access forbidden")

    employer = await employers_collection.find_one({"_id": ObjectId(current_user["id"])})
    if not employer:
        raise HTTPException(status_code=404, detail="Employer not found")

    return {
        "username": employer["username"],
        "email": employer["email"],
        "id": str(employer["_id"]),
    }

# --------------------
# GET /employees
# --------------------
@router.get("/employees")
async def get_employees(current_user: dict = Depends(get_current_user)):
    if current_user["type"] != "employer":
        raise HTTPException(status_code=403, detail="Access forbidden")

    cursor = employees_collection.find({"employer_id": current_user["id"]})
    employees = []

    async for employee in cursor:
        employee_id = str(employee["_id"])

        # Fetch unpaid attendance records only
        attendance_cursor = attendance_collection.find({
            "employee_id": employee_id,
            "paid": False  # ✅ Only unpaid sessions counted
        })

        total_earnings = 0
        last_check_in = None
        is_working = False

        async for record in attendance_cursor:
            if record.get("earnings"):
                total_earnings += record["earnings"]
            if record.get("check_in") and not record.get("check_out"):
                is_working = True
                last_check_in = record.get("check_in")

        employees.append({
            "id": employee_id,
            "username": employee["username"],
            "email": employee["email"],
            "hourly_rate": employee["hourly_rate"],
            "status": "Working" if is_working else "Not Working",
            "last_check_in": last_check_in,
            "total_unpaid_earnings": round(total_earnings, 2)  # ✅ Clear that these are unpaid
        })

    return employees

# --------------------
# POST /pay_employee/{employee_id}
# --------------------
@router.post("/pay_employee/{employee_id}")
async def pay_employee(employee_id: str, authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=403, detail="Authorization token missing")

    current_user = await get_current_user(authorization)

    if current_user["type"] != "employer":
        raise HTTPException(status_code=403, detail="Only employers can mark payment")

    result = await attendance_collection.update_many(
        {"employee_id": employee_id, "paid": False},
        {"$set": {"paid": True}}
    )

    return {"message": f"{result.modified_count} sessions marked as paid."}
