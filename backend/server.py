from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, List
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta, timezone
import jwt
import bcrypt
import uuid
from supabase import create_client, Client

# Load environment variables
load_dotenv()

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase setup
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# JWT Configuration
SECRET_KEY = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

security = HTTPBearer()

# Pydantic Models
class UserBase(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    role: str  # admin, mentor, student

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: str
    role: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserBase

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    role: str

# Course Models
class CourseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    mentor_id: Optional[str] = None
    batch_id: Optional[str] = None
    zoom_id: Optional[str] = None
    teams_id: Optional[str] = None

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    mentor_id: Optional[str] = None
    batch_id: Optional[str] = None
    zoom_id: Optional[str] = None
    teams_id: Optional[str] = None
    video_urls: Optional[List[dict]] = None

class CourseResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    mentor_id: Optional[str] = None
    batch_id: Optional[str] = None
    zoom_id: Optional[str] = None
    teams_id: Optional[str] = None
    approval_status: str
    video_urls: List[dict] = []
    created_at: str
    updated_at: str

class CourseApproval(BaseModel):
    approval_status: str  # approved, rejected, pending

# Enrollment Models
class EnrollmentCreate(BaseModel):
    course_id: str

class EnrollmentResponse(BaseModel):
    id: str
    student_id: str
    course_id: str
    enrollment_date: str
    completion_status: str
    certificate_url: Optional[str] = None

class EnrollmentStatusUpdate(BaseModel):
    completion_status: str  # in_progress, completed, dropped

# Task Models
class TaskCreate(BaseModel):
    course_id: str
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[str] = None

class TaskResponse(BaseModel):
    id: str
    course_id: str
    mentor_id: str
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None
    created_at: str
    updated_at: str

class TaskSubmissionCreate(BaseModel):
    task_id: str
    content: Optional[str] = None
    file_url: Optional[str] = None

class TaskSubmissionResponse(BaseModel):
    id: str
    task_id: str
    student_id: str
    content: Optional[str] = None
    file_url: Optional[str] = None
    submitted_at: str
    grade: Optional[float] = None
    feedback: Optional[str] = None
    updated_at: str

class TaskGrading(BaseModel):
    grade: float
    feedback: Optional[str] = None

# Attendance Models
class AttendanceCreate(BaseModel):
    course_id: str
    date: str

class AttendanceResponse(BaseModel):
    id: str
    student_id: str
    course_id: str
    date: str
    check_in: Optional[str] = None
    check_out: Optional[str] = None
    ai_alerts: List[dict] = []
    created_at: str

# Helper Functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    # Query Supabase for user
    result = supabase.table("users").select("*").eq("id", user_id).execute()
    
    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=401, detail="User not found")
    
    user = result.data[0]
    return UserBase(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        full_name=user["full_name"],
        role=user["role"]
    )

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# Routes
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "LMS Backend with Supabase"}

@app.post("/api/auth/register", response_model=Token)
async def register(user: UserCreate):
    # Check if username exists
    existing_username = supabase.table("users").select("id").eq("username", user.username).execute()
    if existing_username.data and len(existing_username.data) > 0:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check if email exists
    existing_email = supabase.table("users").select("id").eq("email", user.email).execute()
    if existing_email.data and len(existing_email.data) > 0:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Validate role
    if user.role not in ["admin", "mentor", "student"]:
        raise HTTPException(status_code=400, detail="Invalid role. Must be admin, mentor, or student")
    
    # Create new user
    user_id = str(uuid.uuid4())
    hashed_pwd = hash_password(user.password)
    
    new_user = {
        "id": user_id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "password_hash": hashed_pwd,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Insert into Supabase
    result = supabase.table("users").insert(new_user).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create user")
    
    # Create access token
    access_token = create_access_token(data={"sub": user_id, "role": user.role})
    
    user_response = UserBase(
        id=user_id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role
    )
    
    return Token(access_token=access_token, token_type="bearer", user=user_response)

@app.post("/api/auth/login", response_model=Token)
async def login(credentials: UserLogin):
    # Try to find user by username first
    result = supabase.table("users").select("*").eq("username", credentials.username).execute()
    
    # If not found by username, try by email
    if not result.data or len(result.data) == 0:
        result = supabase.table("users").select("*").eq("email", credentials.username).execute()
    
    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=401, detail="Invalid username/email or password")
    
    user = result.data[0]
    
    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username/email or password")
    
    # Create access token
    access_token = create_access_token(data={"sub": user["id"], "role": user["role"]})
    
    user_response = UserBase(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        full_name=user["full_name"],
        role=user["role"]
    )
    
    return Token(access_token=access_token, token_type="bearer", user=user_response)

@app.get("/api/auth/me", response_model=UserResponse)
async def get_me(current_user: UserBase = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role
    )

@app.get("/api/users", response_model=List[UserResponse])
async def get_users(current_user: UserBase = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = supabase.table("users").select("*").execute()
    
    if not result.data:
        return []
    
    return [UserResponse(
        id=u["id"],
        username=u["username"],
        email=u["email"],
        full_name=u["full_name"],
        role=u["role"]
    ) for u in result.data]

# ==================== COURSE MANAGEMENT ENDPOINTS ====================

@app.post("/api/courses", response_model=CourseResponse)
async def create_course(course: CourseCreate, current_user: UserBase = Depends(get_current_user)):
    """Create a new course (Admin or Mentor)"""
    if current_user.role not in ["admin", "mentor"]:
        raise HTTPException(status_code=403, detail="Only admins and mentors can create courses")
    
    course_id = str(uuid.uuid4())
    
    # If mentor is creating, auto-assign to them
    mentor_id = course.mentor_id if course.mentor_id else (current_user.id if current_user.role == "mentor" else None)
    
    new_course = {
        "id": course_id,
        "title": course.title,
        "description": course.description,
        "mentor_id": mentor_id,
        "batch_id": course.batch_id,
        "zoom_id": course.zoom_id,
        "teams_id": course.teams_id,
        "approval_status": "pending",
        "video_urls": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    result = supabase.table("courses").insert(new_course).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create course")
    
    return CourseResponse(**result.data[0])

@app.get("/api/courses", response_model=List[CourseResponse])
async def get_courses(
    approval_status: Optional[str] = None,
    current_user: UserBase = Depends(get_current_user)
):
    """Get all courses based on user role and filters"""
    query = supabase.table("courses").select("*")
    
    # Role-based filtering
    if current_user.role == "student":
        # Students only see approved courses
        query = query.eq("approval_status", "approved")
    elif current_user.role == "mentor":
        # Mentors see approved courses + their own courses (any status)
        # Note: Supabase Python client limitation - we'll fetch all and filter in Python
        pass
    # Admin sees all courses
    
    # Apply approval_status filter if provided
    if approval_status and current_user.role == "admin":
        query = query.eq("approval_status", approval_status)
    
    result = query.execute()
    
    if not result.data:
        return []
    
    courses = result.data
    
    # Additional filtering for mentors
    if current_user.role == "mentor":
        courses = [
            c for c in courses 
            if c["approval_status"] == "approved" or c["mentor_id"] == current_user.id
        ]
    
    return [CourseResponse(**c) for c in courses]

@app.get("/api/courses/{course_id}", response_model=CourseResponse)
async def get_course(course_id: str, current_user: UserBase = Depends(get_current_user)):
    """Get a single course by ID"""
    result = supabase.table("courses").select("*").eq("id", course_id).execute()
    
    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=404, detail="Course not found")
    
    course = result.data[0]
    
    # Check access permissions
    if current_user.role == "student" and course["approval_status"] != "approved":
        raise HTTPException(status_code=403, detail="Access denied")
    
    if current_user.role == "mentor":
        if course["approval_status"] != "approved" and course["mentor_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    return CourseResponse(**course)

@app.put("/api/courses/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: str,
    course_update: CourseUpdate,
    current_user: UserBase = Depends(get_current_user)
):
    """Update a course (Admin or course mentor)"""
    # Get existing course
    result = supabase.table("courses").select("*").eq("id", course_id).execute()
    
    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=404, detail="Course not found")
    
    existing_course = result.data[0]
    
    # Check permissions
    if current_user.role == "mentor" and existing_course["mentor_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="You can only edit your own courses")
    
    if current_user.role not in ["admin", "mentor"]:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    # Build update data
    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
    
    if course_update.title is not None:
        update_data["title"] = course_update.title
    if course_update.description is not None:
        update_data["description"] = course_update.description
    if course_update.mentor_id is not None:
        update_data["mentor_id"] = course_update.mentor_id
    if course_update.batch_id is not None:
        update_data["batch_id"] = course_update.batch_id
    if course_update.zoom_id is not None:
        update_data["zoom_id"] = course_update.zoom_id
    if course_update.teams_id is not None:
        update_data["teams_id"] = course_update.teams_id
    if course_update.video_urls is not None:
        update_data["video_urls"] = course_update.video_urls
    
    result = supabase.table("courses").update(update_data).eq("id", course_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to update course")
    
    return CourseResponse(**result.data[0])

@app.delete("/api/courses/{course_id}")
async def delete_course(course_id: str, current_user: UserBase = Depends(get_current_user)):
    """Delete a course (Admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete courses")
    
    result = supabase.table("courses").delete().eq("id", course_id).execute()
    
    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return {"message": "Course deleted successfully"}

@app.put("/api/courses/{course_id}/approve", response_model=CourseResponse)
async def approve_course(
    course_id: str,
    approval: CourseApproval,
    current_user: UserBase = Depends(get_current_user)
):
    """Approve or reject a course (Admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can approve/reject courses")
    
    if approval.approval_status not in ["approved", "rejected", "pending"]:
        raise HTTPException(status_code=400, detail="Invalid approval status")
    
    update_data = {
        "approval_status": approval.approval_status,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    result = supabase.table("courses").update(update_data).eq("id", course_id).execute()
    
    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return CourseResponse(**result.data[0])

@app.get("/api/courses/mentor/{mentor_id}", response_model=List[CourseResponse])
async def get_mentor_courses(mentor_id: str, current_user: UserBase = Depends(get_current_user)):
    """Get all courses for a specific mentor"""
    # Admins can view any mentor's courses, mentors can only view their own
    if current_user.role == "mentor" and current_user.id != mentor_id:
        raise HTTPException(status_code=403, detail="You can only view your own courses")
    
    if current_user.role == "student":
        raise HTTPException(status_code=403, detail="Students cannot access this endpoint")
    
    result = supabase.table("courses").select("*").eq("mentor_id", mentor_id).execute()
    
    if not result.data:
        return []
    
    return [CourseResponse(**c) for c in result.data]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)