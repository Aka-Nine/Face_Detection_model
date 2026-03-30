<div align="center">

# 🎯 FaceAttend — AI-Powered Attendance Management System

**A full-stack biometric attendance platform powered by deep learning facial recognition**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![React](https://img.shields.io/badge/React-18%2B-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org/)
[![ResNet-34](https://img.shields.io/badge/ResNet--34-Face%20AI-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)](https://github.com/ageitgey/face_recognition)
[![JWT](https://img.shields.io/badge/JWT-Auth-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)](https://jwt.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

<br/>

> **FaceAttend** eliminates manual attendance tracking by combining ResNet-34 deep learning face embeddings with a modern REST API. Employees check in and out using their face — no cards, no PINs, no proxies.

</div>

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Live Demo & Screenshots](#-live-demo--screenshots)
- [Architecture Diagram](#-architecture-diagram)
- [Tech Stack](#-tech-stack)
- [Features](#-features)
- [Project Structure](#-project-structure)
- [How Face Recognition Works](#-how-face-recognition-works)
- [API Reference](#-api-reference)
- [Installation & Setup](#-installation--setup)
- [Environment Variables](#-environment-variables)
- [Face Recognition Tuning](#-face-recognition-tuning)
- [Future Roadmap](#-future-roadmap)
- [Contributing](#-contributing)

---

## 🔍 Overview

FaceAttend is a **full-stack biometric attendance system** built for workplaces that want automated, fraud-resistant employee tracking. The system:

- Registers users with **live face capture**, encoding their biometric data as a 128-dimensional vector using **ResNet-34**
- Authenticates employees at login, check-in, and check-out via **real-time face comparison**
- Tracks **work hours and earnings automatically**
- Provides employers with a **dashboard** for managing employees, monitoring real-time status, and processing payments

The backend is built with **FastAPI** for high-performance async API serving, **Motor** for async MongoDB access, and **face_recognition** (dlib/ResNet-34 under the hood) for all biometric operations.

---

## 🏗 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                                  │
│                                                                      │
│   ┌──────────────────────┐        ┌──────────────────────────────┐  │
│   │   React Frontend     │        │    Grafix Dashboard UI       │  │
│   │  (attendance-system- │        │  (Analytics / Payments /     │  │
│   │    frontend/)        │        │   Employee Management)       │  │
│   └──────────┬───────────┘        └──────────────┬───────────────┘  │
│              │  HTTP / multipart/form-data         │                  │
└──────────────┼─────────────────────────────────────┼─────────────────┘
               │                                     │
               ▼                                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        API GATEWAY LAYER                             │
│                                                                      │
│              FastAPI  +  Uvicorn (ASGI)  — main.py                   │
│         ┌─────────────────────────────────────────────┐             │
│         │            Middleware & DI                   │             │
│         │   JWT Auth Middleware  |  Pydantic Schemas   │             │
│         └─────────────────────────────────────────────┘             │
└────────────────────────────────┬────────────────────────────────────┘
                                 │  Route dispatching
          ┌──────────────────────┼──────────────────────┐
          ▼                      ▼                      ▼
┌─────────────────┐  ┌───────────────────┐  ┌───────────────────────┐
│  employer.py    │  │   employee.py     │  │    attendance.py      │
│                 │  │                   │  │                       │
│ /employer/      │  │ /employee/        │  │ /attendance/checkin   │
│   register      │  │   register        │  │ /attendance/checkout  │
│ /employer/      │  │ /employee/        │  │ /employee/attendance/ │
│   pay_employee  │  │   attendance/     │  │   summary             │
│                 │  │   summary         │  │                       │
└────────┬────────┘  └────────┬──────────┘  └──────────┬────────────┘
         │                    │                         │
         └──────────┬─────────┘                        │
                    ▼                                   ▼
┌─────────────────────────────┐         ┌──────────────────────────────┐
│      auth.py                │         │         utils.py             │
│                             │         │                              │
│  • JWT token generation     │         │  • encode_face_from_image()  │
│  • Token verification       │         │  • hash_password()           │
│  • Role-based middleware     │         │  • verify_password()         │
│  • /login/password          │         │  • image resize & preprocess │
│  • /login/face              │         │                              │
└──────────┬──────────────────┘         └──────────────┬───────────────┘
           │                                           │
           ▼                                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     FACE RECOGNITION ENGINE                          │
│                                                                      │
│   Input Image (multipart/form-data)                                  │
│        │                                                             │
│        ▼                                                             │
│   PIL / OpenCV ──► Resize & Normalize                               │
│        │                                                             │
│        ▼                                                             │
│   face_recognition.face_locations()  ──► Detect face bounding box   │
│        │                                                             │
│        ▼                                                             │
│   face_recognition.face_encodings()  ──► ResNet-34 128D embedding   │
│        │                                                             │
│        ▼                                                             │
│   face_recognition.compare_faces()   ──► Euclidean distance match   │
│   [tolerance: 0.6 for login | 0.65 for check-in/out]                │
│        │                                                             │
│        ▼                                                             │
│   ✅ Match → Proceed   |   ❌ No Match → 401 Unauthorized            │
│                                                                      │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                                    │
│                                                                      │
│        database.py  ──►  Motor (async)  ──►  MongoDB Atlas           │
│                                                                      │
│   Collections:                                                        │
│   ┌────────────────┐  ┌────────────────┐  ┌────────────────────┐    │
│   │   employers    │  │   employees    │  │    attendance      │    │
│   │────────────────│  │────────────────│  │────────────────────│    │
│   │ _id            │  │ _id            │  │ _id                │    │
│   │ name           │  │ name           │  │ employee_id        │    │
│   │ email          │  │ email          │  │ employer_id        │    │
│   │ password_hash  │  │ password_hash  │  │ check_in_time      │    │
│   │ role: employer │  │ role: employee │  │ check_out_time     │    │
│   │ face_encoding  │  │ face_encoding  │  │ hours_worked       │    │
│   │   [128D vec]   │  │   [128D vec]   │  │ earnings           │    │
│   │ created_at     │  │ employer_id    │  │ is_paid            │    │
│   └────────────────┘  │ hourly_rate    │  └────────────────────┘    │
│                        │ created_at     │                            │
│                        └────────────────┘                            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🧰 Tech Stack

### Backend
| Technology | Version | Purpose |
|---|---|---|
| **Python** | 3.10+ | Core language |
| **FastAPI** | 0.100+ | Async REST API framework |
| **Uvicorn** | Latest | ASGI server |
| **Motor** | 3.x | Async MongoDB driver |
| **MongoDB Atlas** | Cloud | NoSQL database |
| **face_recognition** | 1.3.0 | Face encoding & comparison (dlib wrapper) |
| **ResNet-34** | — | Deep learning backbone for face embeddings |
| **dlib** | 19.x | C++ ML library used by face_recognition |
| **OpenCV** | 4.x | Image preprocessing |
| **Pillow (PIL)** | 10.x | Image I/O and resizing |
| **NumPy** | 1.x | Numerical operations on face vectors |
| **PyJWT** | 2.x | JSON Web Token generation & verification |
| **bcrypt** | 4.x | Password hashing |
| **Pydantic** | 2.x | Request/response data validation |
| **python-dotenv** | Latest | Environment variable management |
| **python-multipart** | Latest | File upload support |

### Frontend
| Technology | Purpose |
|---|---|
| **React 18** | UI framework |
| **Grafix Dashboard** | Analytics & management UI |
| **Webcam API** | Live face capture for registration/login |

---

## ✨ Features

### 👤 User Management
- **Employer registration** with facial capture and secure credential storage
- **Employee registration** linked to employer accounts with face onboarding
- **Dual authentication** — email/password OR facial recognition
- **Role-based access control** — employers and employees see different data

### 📋 Attendance Tracking
- **Face-based check-in** — matches live face against stored 128D embedding
- **Face-based check-out** — verifies same employee and closes session
- **Automatic hours calculation** — computed from check-in/check-out timestamps
- **Earnings computation** — `hours_worked × hourly_rate` stored per session

### 🏢 Employer Dashboard
- View all registered employees and their current status (working / not working)
- Browse attendance history per employee
- Mark employees as paid after processing payroll
- Real-time monitoring via Grafix UI

### 🔐 Security
- All passwords hashed with **bcrypt** (no plain-text storage)
- All protected endpoints secured with **JWT Bearer tokens**
- Face encoding tolerance tuned per use case (login vs. daily check-in)
- Face data stored only as numerical vectors — no raw image storage

---

## 📁 Project Structure

```
Face_Detection_model/
│
├── backend/                        # FastAPI application
│   ├── main.py                     # App entrypoint, route registration, CORS
│   ├── auth.py                     # JWT logic, /login/password, /login/face
│   ├── database.py                 # Motor async MongoDB client setup
│   ├── utils.py                    # Face encoding, password hashing helpers
│   ├── models.py                   # Pydantic request/response schemas
│   ├── employee.py                 # Employee registration & attendance summary
│   ├── employer.py                 # Employer registration, employee mgmt, payroll
│   ├── attendance.py               # Check-in / check-out logic
│   └── requirements.txt            # Python dependencies
│
├── attendance-system-frontend/     # React frontend (Grafix Dashboard)
│   └── ...                         # React components, pages, API hooks
│
├── About Project.txt               # Project overview notes
└── README.md                       # This file
```

---

## 🧠 How Face Recognition Works

FaceAttend uses a **ResNet-34 deep residual network** to generate compact 128-dimensional face embeddings. Here is the full pipeline:

### Registration Flow
```
1. User submits registration form + face image (multipart/form-data)
2. Image decoded by PIL and resized for processing
3. face_recognition.face_locations() detects bounding box in image
4. face_recognition.face_encodings() runs ResNet-34 → 128D float vector
5. Vector stored in MongoDB alongside user document
```

### Authentication / Check-in Flow
```
1. User submits live face image
2. New 128D embedding generated from submitted image
3. Stored encoding retrieved from MongoDB
4. face_recognition.compare_faces([stored], new, tolerance=T) called
5. Euclidean distance < tolerance → ✅ Match, JWT issued / attendance logged
6. Euclidean distance ≥ tolerance → ❌ 401 Unauthorized
```

### Tolerance Parameters

| Operation | Tolerance | Rationale |
|---|---|---|
| `/login/face` | **0.6** | Stricter — protects account access |
| `/attendance/checkin` | **0.65** | Slightly lenient — daily use, varied lighting |
| `/attendance/checkout` | **0.65** | Same as check-in |

> A lower tolerance value means stricter matching. `0.6` is the library default and is generally considered secure for authentication.

---

## 📡 API Reference

Base URL: `http://127.0.0.1:8000`

Interactive docs: `http://127.0.0.1:8000/docs` (Swagger UI)

### Auth

| Method | Endpoint | Auth | Body | Description |
|---|---|---|---|---|
| `POST` | `/login/password` | None | `email`, `password` | Login with credentials → JWT |
| `POST` | `/login/face` | None | `image` (file) | Login with face → JWT |

### Employer

| Method | Endpoint | Auth | Body | Description |
|---|---|---|---|---|
| `POST` | `/employer/register` | None | `name`, `email`, `password`, `image` | Register new employer |
| `GET` | `/employer/employees` | JWT (employer) | — | List all employees |
| `POST` | `/employer/pay_employee/{employee_id}` | JWT (employer) | — | Mark employee as paid |

### Employee

| Method | Endpoint | Auth | Body | Description |
|---|---|---|---|---|
| `POST` | `/employee/register` | JWT (employer) | `name`, `email`, `password`, `hourly_rate`, `image` | Register new employee |
| `GET` | `/employee/attendance/summary` | JWT (employee) | — | Personal attendance history |

### Attendance

| Method | Endpoint | Auth | Body | Description |
|---|---|---|---|---|
| `POST` | `/attendance/checkin` | None | `image` (file) | Face check-in → opens session |
| `POST` | `/attendance/checkout` | None | `image` (file) | Face check-out → closes session, calculates hours |

### Response Examples

**POST /login/face** — Success
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "role": "employee",
  "user_id": "64f2a3b1e4b0c1a2d3e4f567"
}
```

**POST /attendance/checkout** — Success
```json
{
  "message": "Check-out successful",
  "hours_worked": 8.25,
  "earnings": 123.75
}
```

---

## ⚙️ Installation & Setup

### Prerequisites

| Requirement | Notes |
|---|---|
| Python 3.10+ | `python --version` |
| CMake | Required to build dlib |
| C++ compiler | gcc / MSVC / Clang |
| MongoDB Atlas account | Or local MongoDB 6+ |
| Node.js 18+ | For the React frontend |

> **Note on dlib**: The `face_recognition` library compiles dlib from source. On Windows, ensure Visual Studio Build Tools are installed. On Linux/Mac, `cmake` and `gcc` must be available.

### 1. Clone the Repository

```bash
git clone https://github.com/Aka-Nine/Face_Detection_model.git
cd Face_Detection_model
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt
```

> If dlib fails to install, try: `pip install dlib --verbose` after installing cmake

### 3. Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```env
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/
DATABASE_NAME=attendance_system
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 4. Run the Backend

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API is live at: **http://127.0.0.1:8000**  
Swagger docs at: **http://127.0.0.1:8000/docs**

### 5. Frontend Setup

```bash
cd ../attendance-system-frontend
npm install
npm start
```

Frontend runs at: **http://localhost:3000**

---

## 🔐 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `MONGO_URI` | ✅ | MongoDB Atlas connection string |
| `DATABASE_NAME` | ✅ | MongoDB database name |
| `SECRET_KEY` | ✅ | JWT signing secret (use a long random string in production) |
| `ALGORITHM` | Optional | JWT algorithm (default: `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Optional | Token expiry in minutes (default: `60`) |

---

## 🎛 Face Recognition Tuning

The tolerance value controls how strict the face match must be:

```python
# In utils.py / auth.py
face_recognition.compare_faces([stored_encoding], new_encoding, tolerance=0.6)
```

| Tolerance | Behavior | Recommended For |
|---|---|---|
| `0.4` | Very strict — may reject valid users | High-security scenarios |
| `0.6` | Balanced (library default) | Login authentication |
| `0.65` | More lenient | Daily check-in/out |
| `0.7+` | Loose — may allow false positives | Not recommended |

**Tips for better accuracy:**
- Use well-lit, frontal face images during registration
- Capture 2–3 encodings per user and average them for robustness
- Use consistent camera distance (face fills 30–70% of frame)

---

## 🗺 Future Roadmap

- [ ] **Multi-face encoding** — capture 3 angles during registration for improved accuracy
- [ ] **Anti-spoofing** — detect printed photos or screen-displayed faces
- [ ] **Rate limiting** — prevent brute-force face injection attacks
- [ ] **Comprehensive logging** — structured logs with middleware
- [ ] **Dockerization** — `docker-compose.yml` for backend + MongoDB
- [ ] **WebSocket support** — real-time check-in notifications on dashboard
- [ ] **Attendance reports** — exportable CSV / PDF payroll summaries
- [ ] **Mobile app** — React Native client with camera integration
- [ ] **Unit & integration tests** — pytest test suite for all routes

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m "feat: add your feature"`
4. Push to branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ using FastAPI, ResNet-34, and MongoDB**

*If you found this useful, consider giving the repo a ⭐*

</div>
