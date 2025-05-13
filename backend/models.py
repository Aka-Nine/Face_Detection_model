from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

class EmployerCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    face_encoding: Optional[List[float]]  # Store face encoding as a list of floats

class EmployerLogin(BaseModel):
    email: EmailStr
    password: str

class EmployeeCreate(BaseModel):
    employer_id: str
    email: EmailStr
    username: str
    password: str
    hourly_rate: float
    face_encoding: Optional[List[float]]  # Store face encoding

class EmployeeLogin(BaseModel):
    email: EmailStr
    password: str

class FaceLogin(BaseModel):
    image: bytes  # Base64 encoded image for login

class Attendance(BaseModel):
    employee_id: str
    check_in: datetime
    check_out: Optional[datetime] = None
    hours_worked: Optional[float] = None
    earnings: Optional[float] = None
