import cv2
import numpy as np
import face_recognition
from fastapi import HTTPException
from passlib.context import CryptContext  # For password hashing
from PIL import Image
from io import BytesIO

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a plain text password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against a hashed one."""
    return pwd_context.verify(plain_password, hashed_password)

def get_face_encoding(image_bytes: bytes):
    """Extract face encoding from an uploaded image."""
    try:
        # Open image safely
        image = Image.open(BytesIO(image_bytes)).convert('RGB')

        # Resize to 640x480 for standard size (faster and consistent)
        image = image.resize((640, 480))

        # Convert to numpy array
        np_image = np.array(image)

        # Detect faces
        face_locations = face_recognition.face_locations(np_image)
        if not face_locations:
            raise HTTPException(status_code=400, detail="No face detected. Please upload a clear front-facing image.")

        # Generate encodings
        face_encodings = face_recognition.face_encodings(np_image, face_locations)
        if not face_encodings:
            raise HTTPException(status_code=400, detail="Face detected but encoding failed.")

        return face_encodings[0].tolist()  # Return as list (MongoDB-friendly)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Image processing error: {str(e)}")

def compare_faces(known_encodings, unknown_encoding, tolerance: float = 0.6):
    """Compare an unknown face encoding with known ones."""
    try:
        known_encodings = [np.array(encoding, dtype=np.float64) for encoding in known_encodings]
        unknown_encoding = np.array(unknown_encoding, dtype=np.float64)

        matches = face_recognition.compare_faces(known_encodings, unknown_encoding, tolerance=tolerance)
        return any(matches)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Face comparison error: {str(e)}")
