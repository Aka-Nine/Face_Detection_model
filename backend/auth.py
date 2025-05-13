import os
import jwt
import numpy as np
from fastapi import HTTPException, Depends, UploadFile, Form, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from bson import ObjectId

from database import employees_collection, employers_collection
from utils import get_face_encoding, compare_faces, hash_password, verify_password

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict, expires_delta: timedelta = None):
    """Generate a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    """Decode a JWT token and return its payload."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError as e:
        print("❌ JWT decode error:", str(e))
        return None


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Retrieve the current user from the token and fetch user details from the database."""
    payload = decode_token(token)
    print("🔍 Token payload:", payload)

    if payload is None or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")

    user_id = payload["sub"]
    user_type = payload.get("type", "employee")  # Default to employee

    try:
        user_id = ObjectId(user_id)
    except Exception:
        print("❌ Invalid ObjectId:", user_id)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format")

    collection = employees_collection if user_type == "employee" else employers_collection
    user = await collection.find_one({"_id": user_id})

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return {
        "id": str(user["_id"]),
        "username": user.get("username"),
        "email": user.get("email"),
        "type": user_type
    }


# -------------------------------
# LOGIN with Email & Password
# -------------------------------
async def login_with_password(email: str = Form(...), password: str = Form(...)):
    """Authenticate an employer or employee using email and password."""
    user = await employers_collection.find_one({"email": email})
    user_type = "employer"

    if not user:
        user = await employees_collection.find_one({"email": email})
        user_type = "employee"

    if not user or not verify_password(password, user["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = create_access_token({"sub": str(user["_id"]), "type": user_type})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_type": user_type,
        "username": user["username"],
        "email": user["email"]
    }


# -------------------------------
# LOGIN with Face (General)
# -------------------------------
async def login_with_face(image: UploadFile):
    """Authenticate a user (employee or employer) using face recognition."""
    image_bytes = await image.read()

    try:
        unknown_encoding = get_face_encoding(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")

    if not unknown_encoding:
        raise HTTPException(status_code=400, detail="No face detected in the uploaded image.")

    unknown_encoding = np.array(unknown_encoding, dtype=np.float64)

    # Try employees
    async for employee in employees_collection.find({"face_encoding": {"$exists": True}}):
        stored_encoding = employee.get("face_encoding")
        if stored_encoding:
            stored_encoding = np.array(stored_encoding, dtype=np.float64)
            if compare_faces([stored_encoding], unknown_encoding):
                token = create_access_token({"sub": str(employee["_id"]), "type": "employee"})
                return {
                    "access_token": token,
                    "token_type": "bearer",
                    "user_type": "employee",
                    "username": employee["username"],
                    "email": employee["email"]
                }

    # Try employers
    async for employer in employers_collection.find({"face_encoding": {"$exists": True}}):
        stored_encoding = employer.get("face_encoding")
        if stored_encoding:
            stored_encoding = np.array(stored_encoding, dtype=np.float64)
            if compare_faces([stored_encoding], unknown_encoding):
                token = create_access_token({"sub": str(employer["_id"]), "type": "employer"})
                return {
                    "access_token": token,
                    "token_type": "bearer",
                    "user_type": "employer",
                    "username": employer["username"],
                    "email": employer["email"]
                }

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Face not recognized")


# -------------------------------
# LOGIN with Face (Employee Only)
# -------------------------------
async def login_employee_with_face(image: UploadFile):
    """Authenticate an employee using face recognition."""
    image_bytes = await image.read()

    try:
        unknown_encoding = get_face_encoding(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")

    if not unknown_encoding:
        raise HTTPException(status_code=400, detail="No face detected in the uploaded image.")

    unknown_encoding = np.array(unknown_encoding, dtype=np.float64)

    async for employee in employees_collection.find({"face_encoding": {"$exists": True}}):
        stored_encoding = employee.get("face_encoding")
        if stored_encoding:
            stored_encoding = np.array(stored_encoding, dtype=np.float64)
            if compare_faces([stored_encoding], unknown_encoding):
                token = create_access_token({"sub": str(employee["_id"]), "type": "employee"})
                return {
                    "access_token": token,
                    "token_type": "bearer",
                    "user_type": "employee",
                    "username": employee["username"],
                    "email": employee["email"]
                }

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Face not recognized")


# -------------------------------
# LOGIN with Face (Employer Only)
# -------------------------------
async def login_employer_with_face(image: UploadFile):
    """Authenticate an employer using face recognition."""
    image_bytes = await image.read()

    try:
        unknown_encoding = get_face_encoding(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")

    if not unknown_encoding:
        raise HTTPException(status_code=400, detail="No face detected in the uploaded image.")

    unknown_encoding = np.array(unknown_encoding, dtype=np.float64)

    async for employer in employers_collection.find({"face_encoding": {"$exists": True}}):
        stored_encoding = employer.get("face_encoding")
        if stored_encoding:
            stored_encoding = np.array(stored_encoding, dtype=np.float64)
            if compare_faces([stored_encoding], unknown_encoding):
                token = create_access_token({"sub": str(employer["_id"]), "type": "employer"})
                return {
                    "access_token": token,
                    "token_type": "bearer",
                    "user_type": "employer",
                    "username": employer["username"],
                    "email": employer["email"]
                }

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Face not recognized")
