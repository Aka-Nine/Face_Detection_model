from fastapi import APIRouter, UploadFile, File, HTTPException, Header
from datetime import datetime
import numpy as np

from database import attendance_collection, employees_collection
from utils import get_face_encoding, compare_faces
from auth import decode_token
from bson import ObjectId

router = APIRouter()


async def get_user_from_token(authorization: str):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=403, detail="Invalid or missing authorization token")

    token = authorization.split(" ")[1]
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    user_id = payload["sub"]
    try:
        user_obj_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    user = await employees_collection.find_one({"_id": user_obj_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.post("/checkin")
async def check_in(image: UploadFile = File(...), authorization: str = Header(None)):
    user = await get_user_from_token(authorization)

    image_bytes = await image.read()
    try:
        face_encoding = get_face_encoding(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    face_encoding = np.array(face_encoding, dtype=np.float64)
    stored_encoding = np.array(user["face_encoding"], dtype=np.float64)

    match = compare_faces([stored_encoding], face_encoding, tolerance=0.65)
    if not match:
        raise HTTPException(status_code=401, detail="Face not recognized")

    existing = await attendance_collection.find_one({
        "employee_id": str(user["_id"]),
        "check_out": None
    })
    if existing:
        raise HTTPException(status_code=400, detail="Already checked in")

    now = datetime.utcnow()
    await attendance_collection.insert_one({
        "employee_id": str(user["_id"]),
        "check_in": now,
        "check_out": None,
        "hours_worked": None,
        "earnings": None,
        "paid": False
    })
    return {"message": "Check-in successful", "check_in": now}


@router.post("/checkout")
async def check_out(image: UploadFile = File(...), authorization: str = Header(None)):
    user = await get_user_from_token(authorization)

    image_bytes = await image.read()
    try:
        face_encoding = get_face_encoding(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    face_encoding = np.array(face_encoding, dtype=np.float64)
    stored_encoding = np.array(user["face_encoding"], dtype=np.float64)

    match = compare_faces([stored_encoding], face_encoding, tolerance=0.65)
    if not match:
        raise HTTPException(status_code=401, detail="Face not recognized")

    session = await attendance_collection.find_one({
        "employee_id": str(user["_id"]),
        "check_out": None
    })
    if not session:
        raise HTTPException(status_code=404, detail="No active check-in found")

    check_in_time = session["check_in"]
    check_out_time = datetime.utcnow()
    hours = (check_out_time - check_in_time).total_seconds() / 3600
    rate = user.get("hourly_rate", 0)
    earnings = round(hours * rate, 2)

    await attendance_collection.update_one(
        {"_id": session["_id"]},
        {"$set": {
            "check_out": check_out_time,
            "hours_worked": round(hours, 2),
            "earnings": earnings,
            "paid": False
        }}
    )

    return {
        "message": "Check-out successful",
        "hours_worked": round(hours, 2),
        "earnings": earnings,
        "check_out": check_out_time
    }
