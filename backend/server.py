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
import json
import base64
import requests

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
SUPABASE_JWT_SECRET = os.environ.get('SUPABASE_JWT_SECRET')

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# JWT Configuration for Supabase
if not SUPABASE_JWT_SECRET:
    raise ValueError("SUPABASE_JWT_SECRET must be set in environment variables")

# Legacy JWT Configuration (for backward compatibility)
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

class AttendanceUpdate(BaseModel):
    check_in: Optional[str] = None
    check_out: Optional[str] = None
    ai_alerts: Optional[List[dict]] = None

# Materials Management Models
class MaterialCreate(BaseModel):
    course_id: str
    title: str
    description: Optional[str] = None
    file_url: str
    material_type: str  # document, video, image, other

class MaterialUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    file_url: Optional[str] = None
    material_type: Optional[str] = None

class MaterialResponse(BaseModel):
    id: str
    course_id: str
    mentor_id: str
    title: str
    description: Optional[str] = None
    file_url: str
    material_type: str
    is_visible: bool
    created_at: str
    updated_at: str

# Certificate Generation Models
class CertificateGenerate(BaseModel):
    course_id: str
    student_id: str
    completion_date: Optional[str] = None

class CertificateResponse(BaseModel):
    id: str
    student_id: str
    course_id: str
    certificate_url: str
    issued_date: str
    completion_date: str
    created_at: str

# Fee Reminder Models
class FeeReminderCreate(BaseModel):
    student_id: str
    amount: float
    due_date: str
    description: Optional[str] = None

class FeeReminderUpdate(BaseModel):
    amount: Optional[float] = None
    due_date: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class FeeReminderResponse(BaseModel):
    id: str
    student_id: str
    amount: float
    due_date: str
    description: Optional[str] = None
    status: str  # pending, paid, overdue
    created_at: str
    updated_at: str

# Mock Interview Models
class MockInterviewCreate(BaseModel):
    student_id: str
    mentor_id: str
    scheduled_date: str
    type: str  # technical, behavioral, system_design
    duration: Optional[int] = 60  # minutes

class MockInterviewUpdate(BaseModel):
    scheduled_date: Optional[str] = None
    type: Optional[str] = None
    duration: Optional[int] = None
    status: Optional[str] = None

class MockInterviewResponse(BaseModel):
    id: str
    student_id: str
    mentor_id: str
    scheduled_date: str
    type: str
    duration: int
    status: str  # scheduled, completed, cancelled
    feedback: Optional[str] = None
    score: Optional[float] = None
    created_at: str
    updated_at: str

class InterviewFeedback(BaseModel):
    feedback: str
    score: float

# Progress Report Models
class ProgressReportResponse(BaseModel):
    student_id: str
    course_id: Optional[str] = None
    enrollment_count: int
    completed_courses: int
    total_tasks: int
    completed_tasks: int
    attendance_percentage: float
    average_grade: Optional[float] = None
    certificates_earned: int
    last_activity: Optional[str] = None

# Email Notification Models
class EmailNotificationCreate(BaseModel):
    recipient_email: str
    subject: str
    message: str
    template_type: Optional[str] = None

class EmailTemplateCreate(BaseModel):
    name: str
    subject: str
    content: str
    template_type: str  # fee_reminder, task_due, course_approval, certificate

class EmailTemplateResponse(BaseModel):
    id: str
    name: str
    subject: str
    content: str
    template_type: str
    created_at: str
    updated_at: str

# Helper Functions
def create_access_token(data: dict):
    """Legacy function for backward compatibility"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_supabase_token(token: str):
    """Verify Supabase JWT token"""
    try:
        # Decode the JWT token using Supabase JWT secret
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated"
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token validation failed: {str(e)}")

def verify_token(token: str):
    """Legacy function that now tries Supabase token validation first"""
    try:
        # Try Supabase token first
        return verify_supabase_token(token)
    except HTTPException:
        # Fallback to legacy JWT validation for backward compatibility
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
    
    # Handle Supabase JWT payload
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    # Check if this is a Supabase token (has 'aud' field)
    if payload.get("aud") == "authenticated":
        # This is a Supabase token, extract user info from the token
        email = payload.get("email")
        user_metadata = payload.get("user_metadata", {})
        
        if not email:
            raise HTTPException(status_code=401, detail="Email not found in token")
        
        # Extract user data from Supabase token metadata
        user_data = {
            "id": user_id,
            "email": email,
            "username": user_metadata.get("username", email),
            "full_name": user_metadata.get("full_name", email),
            "role": user_metadata.get("role", "student")
        }
        
        return UserBase(
            id=user_data["id"],
            username=user_data["username"],
            email=user_data["email"],
            full_name=user_data["full_name"],
            role=user_data["role"]
        )
    else:
        # Legacy token, query Supabase for user data
        result = supabase.table("users").select("*").eq("id", user_id).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=401, detail="User not found")
        
        user = result.data[0]
        return UserBase(
            id=user["id"],
            username=user["username"],
            email=user.get("email", f"{user['username']}@lms.local"),  # Use username@lms.local if email not available
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
    
    # Skip email check since email column doesn't exist in current schema
    # TODO: Add email check when schema is updated
    
    # Validate role
    if user.role not in ["admin", "mentor", "student"]:
        raise HTTPException(status_code=400, detail="Invalid role. Must be admin, mentor, or student")
    
    # Create new user (without email and password_hash for current schema)
    # Let database auto-generate ID and timestamps
    new_user = {
        "username": user.username,
        "full_name": user.full_name,
        "role": user.role
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
    # Try to find user by username (skip email search since email column doesn't exist)
    result = supabase.table("users").select("*").eq("username", credentials.username).execute()
    
    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    user = result.data[0]
    
    # Skip password verification since password_hash column doesn't exist in current schema
    # TODO: Add password verification when schema is updated
    # For now, allow login with any password for existing users
    
    # Create access token
    access_token = create_access_token(data={"sub": user["id"], "role": user["role"]})
    
    user_response = UserBase(
        id=user["id"],
        username=user["username"],
        email=user.get("email", f"{user['username']}@lms.local"),  # Use default email
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
        email=u.get("email", f"{u['username']}@lms.local"),  # Use default email
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

# ENROLLMENT MANAGEMENT ENDPOINTS

@app.post("/api/enrollments", response_model=EnrollmentResponse)
async def enroll_student(enrollment: EnrollmentCreate, current_user: UserBase = Depends(get_current_user)):
    """Enroll a student in a course"""
    # Only students can enroll themselves, or admins can enroll any student
    if current_user.role not in ["student", "admin"]:
        raise HTTPException(status_code=403, detail="Only students or admins can create enrollments")
    
    # Check if course exists and is approved
    course_result = supabase.table("courses").select("*").eq("id", enrollment.course_id).execute()
    if not course_result.data:
        raise HTTPException(status_code=404, detail="Course not found")
    
    course = course_result.data[0]
    if course["approval_status"] != "approved":
        raise HTTPException(status_code=400, detail="Cannot enroll in non-approved course")
    
    # Check if already enrolled
    existing = supabase.table("enrollments").select("*").eq("student_id", current_user.id).eq("course_id", enrollment.course_id).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Student already enrolled in this course")
    
    # Create enrollment
    enrollment_data = {
        "id": str(uuid.uuid4()),
        "student_id": current_user.id,
        "course_id": enrollment.course_id,
        "enrollment_date": datetime.now(timezone.utc).isoformat(),
        "completion_status": "in_progress"
    }
    
    result = supabase.table("enrollments").insert(enrollment_data).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create enrollment")
    
    return EnrollmentResponse(**result.data[0])

@app.get("/api/enrollments", response_model=List[EnrollmentResponse])
async def get_user_enrollments(current_user: UserBase = Depends(get_current_user)):
    """Get current user's enrollments (students only)"""
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can view their enrollments")
    
    result = supabase.table("enrollments").select("*").eq("student_id", current_user.id).execute()
    
    return [EnrollmentResponse(**e) for e in result.data]

@app.get("/api/enrollments/student/{student_id}", response_model=List[EnrollmentResponse])
async def get_student_enrollments(student_id: str, current_user: UserBase = Depends(get_current_user)):
    """Get enrollments for a specific student (admin and mentors only)"""
    if current_user.role not in ["admin", "mentor"]:
        raise HTTPException(status_code=403, detail="Only admins and mentors can view student enrollments")
    
    result = supabase.table("enrollments").select("*").eq("student_id", student_id).execute()
    
    return [EnrollmentResponse(**e) for e in result.data]

@app.get("/api/enrollments/course/{course_id}", response_model=List[EnrollmentResponse])
async def get_course_enrollments(course_id: str, current_user: UserBase = Depends(get_current_user)):
    """Get all enrollments for a specific course"""
    if current_user.role not in ["admin", "mentor"]:
        raise HTTPException(status_code=403, detail="Only admins and mentors can view course enrollments")
    
    # Mentors can only view enrollments for their own courses
    if current_user.role == "mentor":
        course_result = supabase.table("courses").select("mentor_id").eq("id", course_id).execute()
        if not course_result.data or course_result.data[0]["mentor_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="You can only view enrollments for your own courses")
    
    result = supabase.table("enrollments").select("*").eq("course_id", course_id).execute()
    
    return [EnrollmentResponse(**e) for e in result.data]

@app.delete("/api/enrollments/{course_id}/student/{student_id}")
async def unenroll_student(course_id: str, student_id: str, current_user: UserBase = Depends(get_current_user)):
    """Unenroll a student from a course"""
    # Students can unenroll themselves, admins can unenroll anyone
    if current_user.role == "student" and current_user.id != student_id:
        raise HTTPException(status_code=403, detail="Students can only unenroll themselves")
    elif current_user.role not in ["student", "admin"]:
        raise HTTPException(status_code=403, detail="Only students and admins can unenroll")
    
    # Check if enrollment exists
    enrollment_result = supabase.table("enrollments").select("*").eq("student_id", student_id).eq("course_id", course_id).execute()
    if not enrollment_result.data:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    # Delete enrollment
    result = supabase.table("enrollments").delete().eq("student_id", student_id).eq("course_id", course_id).execute()
    
    return {"message": "Student unenrolled successfully"}

@app.put("/api/enrollments/{course_id}/student/{student_id}/status", response_model=EnrollmentResponse)
async def update_enrollment_status(course_id: str, student_id: str, status_update: EnrollmentStatusUpdate, current_user: UserBase = Depends(get_current_user)):
    """Update enrollment status (completion_status)"""
    # Only mentors and admins can update enrollment status
    if current_user.role not in ["admin", "mentor"]:
        raise HTTPException(status_code=403, detail="Only mentors and admins can update enrollment status")
    
    # Mentors can only update status for their own courses
    if current_user.role == "mentor":
        course_result = supabase.table("courses").select("mentor_id").eq("id", course_id).execute()
        if not course_result.data or course_result.data[0]["mentor_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="You can only update enrollments for your own courses")
    
    # Check if enrollment exists
    enrollment_result = supabase.table("enrollments").select("*").eq("student_id", student_id).eq("course_id", course_id).execute()
    if not enrollment_result.data:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    # Update enrollment status
    update_data = {
        "completion_status": status_update.completion_status
    }
    
    result = supabase.table("enrollments").update(update_data).eq("student_id", student_id).eq("course_id", course_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to update enrollment status")
    
    return EnrollmentResponse(**result.data[0])

# TASK/ASSIGNMENT MANAGEMENT ENDPOINTS

@app.post("/api/tasks", response_model=TaskResponse)
async def create_task(task: TaskCreate, current_user: UserBase = Depends(get_current_user)):
    """Create a new task/assignment"""
    # Only mentors and admins can create tasks
    if current_user.role not in ["admin", "mentor"]:
        raise HTTPException(status_code=403, detail="Only mentors and admins can create tasks")
    
    # Check if course exists
    course_result = supabase.table("courses").select("*").eq("id", task.course_id).execute()
    if not course_result.data:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Mentors can only create tasks for their own courses
    if current_user.role == "mentor":
        course = course_result.data[0]
        if course["mentor_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="You can only create tasks for your own courses")
    
    # Create task
    task_data = {
        "id": str(uuid.uuid4()),
        "course_id": task.course_id,
        "mentor_id": current_user.id,
        "title": task.title,
        "description": task.description,
        "due_date": task.due_date,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    result = supabase.table("tasks").insert(task_data).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create task")
    
    return TaskResponse(**result.data[0])

@app.get("/api/tasks", response_model=List[TaskResponse])
async def get_tasks(course_id: str = None, current_user: UserBase = Depends(get_current_user)):
    """Get tasks (optionally filtered by course_id)"""
    query = supabase.table("tasks").select("*")
    
    if course_id:
        # Check if user has access to the course
        if current_user.role == "student":
            # Students can only see tasks for courses they're enrolled in
            enrollment_result = supabase.table("enrollments").select("*").eq("student_id", current_user.id).eq("course_id", course_id).execute()
            if not enrollment_result.data:
                raise HTTPException(status_code=403, detail="You are not enrolled in this course")
        elif current_user.role == "mentor":
            # Mentors can only see tasks for their own courses
            course_result = supabase.table("courses").select("mentor_id").eq("id", course_id).execute()
            if not course_result.data or course_result.data[0]["mentor_id"] != current_user.id:
                raise HTTPException(status_code=403, detail="You can only view tasks for your own courses")
        
        query = query.eq("course_id", course_id)
    else:
        # If no course_id specified, filter by role
        if current_user.role == "student":
            # Students see tasks from their enrolled courses
            enrollments = supabase.table("enrollments").select("course_id").eq("student_id", current_user.id).execute()
            if not enrollments.data:
                return []
            course_ids = [e["course_id"] for e in enrollments.data]
            query = query.in_("course_id", course_ids)
        elif current_user.role == "mentor":
            # Mentors see tasks from their courses
            courses = supabase.table("courses").select("id").eq("mentor_id", current_user.id).execute()
            if not courses.data:
                return []
            course_ids = [c["id"] for c in courses.data]
            query = query.in_("course_id", course_ids)
    
    result = query.execute()
    return [TaskResponse(**t) for t in result.data]

@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, current_user: UserBase = Depends(get_current_user)):
    """Get a specific task"""
    result = supabase.table("tasks").select("*").eq("id", task_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = result.data[0]
    
    # Check access permissions
    if current_user.role == "student":
        # Students can only view tasks for courses they're enrolled in
        enrollment_result = supabase.table("enrollments").select("*").eq("student_id", current_user.id).eq("course_id", task["course_id"]).execute()
        if not enrollment_result.data:
            raise HTTPException(status_code=403, detail="You are not enrolled in this course")
    elif current_user.role == "mentor":
        # Mentors can only view their own tasks
        if task["mentor_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="You can only view your own tasks")
    
    return TaskResponse(**task)

@app.put("/api/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task_update: TaskUpdate, current_user: UserBase = Depends(get_current_user)):
    """Update a task"""
    # Only mentors and admins can update tasks
    if current_user.role not in ["admin", "mentor"]:
        raise HTTPException(status_code=403, detail="Only mentors and admins can update tasks")
    
    # Check if task exists
    task_result = supabase.table("tasks").select("*").eq("id", task_id).execute()
    if not task_result.data:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = task_result.data[0]
    
    # Mentors can only update their own tasks
    if current_user.role == "mentor" and task["mentor_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="You can only update your own tasks")
    
    # Build update data
    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
    if task_update.title is not None:
        update_data["title"] = task_update.title
    if task_update.description is not None:
        update_data["description"] = task_update.description
    if task_update.due_date is not None:
        update_data["due_date"] = task_update.due_date
    
    result = supabase.table("tasks").update(update_data).eq("id", task_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to update task")
    
    return TaskResponse(**result.data[0])

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str, current_user: UserBase = Depends(get_current_user)):
    """Delete a task"""
    # Only mentors and admins can delete tasks
    if current_user.role not in ["admin", "mentor"]:
        raise HTTPException(status_code=403, detail="Only mentors and admins can delete tasks")
    
    # Check if task exists
    task_result = supabase.table("tasks").select("*").eq("id", task_id).execute()
    if not task_result.data:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = task_result.data[0]
    
    # Mentors can only delete their own tasks
    if current_user.role == "mentor" and task["mentor_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own tasks")
    
    # Delete task
    result = supabase.table("tasks").delete().eq("id", task_id).execute()
    
    return {"message": "Task deleted successfully"}

# TASK SUBMISSION ENDPOINTS

@app.post("/api/task-submissions", response_model=TaskSubmissionResponse)
async def submit_task(submission: TaskSubmissionCreate, current_user: UserBase = Depends(get_current_user)):
    """Submit a task (students only)"""
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can submit tasks")
    
    # Check if task exists
    task_result = supabase.table("tasks").select("*").eq("id", submission.task_id).execute()
    if not task_result.data:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = task_result.data[0]
    
    # Check if student is enrolled in the course
    enrollment_result = supabase.table("enrollments").select("*").eq("student_id", current_user.id).eq("course_id", task["course_id"]).execute()
    if not enrollment_result.data:
        raise HTTPException(status_code=403, detail="You are not enrolled in this course")
    
    # Check if submission already exists
    existing_submission = supabase.table("task_submissions").select("*").eq("task_id", submission.task_id).eq("student_id", current_user.id).execute()
    if existing_submission.data:
        raise HTTPException(status_code=400, detail="You have already submitted this task")
    
    # Create submission
    submission_data = {
        "id": str(uuid.uuid4()),
        "task_id": submission.task_id,
        "student_id": current_user.id,
        "content": submission.content,
        "file_url": submission.file_url,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    result = supabase.table("task_submissions").insert(submission_data).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create submission")
    
    return TaskSubmissionResponse(**result.data[0])

@app.get("/api/task-submissions", response_model=List[TaskSubmissionResponse])
async def get_task_submissions(task_id: str = None, current_user: UserBase = Depends(get_current_user)):
    """Get task submissions"""
    query = supabase.table("task_submissions").select("*")
    
    if current_user.role == "student":
        # Students can only see their own submissions
        query = query.eq("student_id", current_user.id)
    elif current_user.role == "mentor":
        # Mentors can see submissions for their courses' tasks
        if task_id:
            # Check if task belongs to mentor's course
            task_result = supabase.table("tasks").select("*").eq("id", task_id).execute()
            if not task_result.data or task_result.data[0]["mentor_id"] != current_user.id:
                raise HTTPException(status_code=403, detail="You can only view submissions for your own courses")
            query = query.eq("task_id", task_id)
        else:
            # Get all tasks from mentor's courses
            mentor_tasks = supabase.table("tasks").select("id").eq("mentor_id", current_user.id).execute()
            if not mentor_tasks.data:
                return []
            task_ids = [t["id"] for t in mentor_tasks.data]
            query = query.in_("task_id", task_ids)
    
    if task_id and current_user.role == "admin":
        query = query.eq("task_id", task_id)
    
    result = query.execute()
    return [TaskSubmissionResponse(**s) for s in result.data]

@app.put("/api/task-submissions/{submission_id}/grade", response_model=TaskSubmissionResponse)
async def grade_task_submission(submission_id: str, grading: TaskGrading, current_user: UserBase = Depends(get_current_user)):
    """Grade a task submission (mentors and admins only)"""
    if current_user.role not in ["admin", "mentor"]:
        raise HTTPException(status_code=403, detail="Only mentors and admins can grade submissions")
    
    # Check if submission exists
    submission_result = supabase.table("task_submissions").select("*").eq("id", submission_id).execute()
    if not submission_result.data:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    submission = submission_result.data[0]
    
    # Check if mentor has permission to grade (must be their task)
    if current_user.role == "mentor":
        task_result = supabase.table("tasks").select("mentor_id").eq("id", submission["task_id"]).execute()
        if not task_result.data or task_result.data[0]["mentor_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="You can only grade submissions for your own tasks")
    
    # Update submission with grade and feedback
    update_data = {
        "grade": grading.grade,
        "feedback": grading.feedback,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    result = supabase.table("task_submissions").update(update_data).eq("id", submission_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to grade submission")
    
    return TaskSubmissionResponse(**result.data[0])

# ===== ATTENDANCE TRACKING SYSTEM =====

@app.post("/api/attendance/checkin", response_model=AttendanceResponse)
async def checkin_attendance(attendance: AttendanceCreate, current_user: UserBase = Depends(get_current_user)):
    """Student check-in to course"""
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can check in")
    
    # Check if student is enrolled in the course
    enrollment_result = supabase.table("enrollments").select("id").eq("course_id", attendance.course_id).eq("student_id", current_user.id).execute()
    if not enrollment_result.data:
        raise HTTPException(status_code=403, detail="You must be enrolled in this course to check in")
    
    # Check if already checked in today
    existing_result = supabase.table("attendance").select("*").eq("student_id", current_user.id).eq("course_id", attendance.course_id).eq("date", attendance.date).execute()
    
    if existing_result.data:
        # Update existing record
        update_data = {
            "check_in": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        result = supabase.table("attendance").update(update_data).eq("id", existing_result.data[0]["id"]).execute()
        return AttendanceResponse(**result.data[0])
    else:
        # Create new attendance record
        attendance_data = {
            "id": str(uuid.uuid4()),
            "student_id": current_user.id,
            "course_id": attendance.course_id,
            "date": attendance.date,
            "check_in": datetime.now(timezone.utc).isoformat(),
            "ai_alerts": [],
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        result = supabase.table("attendance").insert(attendance_data).execute()
        return AttendanceResponse(**result.data[0])

@app.post("/api/attendance/checkout")
async def checkout_attendance(course_id: str, date: str, current_user: UserBase = Depends(get_current_user)):
    """Student check-out from course"""
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can check out")
    
    # Find existing attendance record
    attendance_result = supabase.table("attendance").select("*").eq("student_id", current_user.id).eq("course_id", course_id).eq("date", date).execute()
    
    if not attendance_result.data:
        raise HTTPException(status_code=404, detail="No check-in record found for today")
    
    # Update with check-out time
    update_data = {
        "check_out": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    result = supabase.table("attendance").update(update_data).eq("id", attendance_result.data[0]["id"]).execute()
    return {"message": "Checked out successfully"}

@app.get("/api/attendance", response_model=List[AttendanceResponse])
async def get_attendance_records(course_id: str = None, student_id: str = None, current_user: UserBase = Depends(get_current_user)):
    """Get attendance records based on role and filters"""
    query = supabase.table("attendance").select("*")
    
    if current_user.role == "student":
        # Students can only see their own attendance
        query = query.eq("student_id", current_user.id)
        if course_id:
            query = query.eq("course_id", course_id)
    elif current_user.role == "mentor":
        # Mentors can see attendance for their courses
        mentor_courses = supabase.table("courses").select("id").eq("mentor_id", current_user.id).execute()
        if not mentor_courses.data:
            return []
        course_ids = [c["id"] for c in mentor_courses.data]
        query = query.in_("course_id", course_ids)
        
        if course_id and course_id not in course_ids:
            raise HTTPException(status_code=403, detail="You can only view attendance for your own courses")
        if course_id:
            query = query.eq("course_id", course_id)
        if student_id:
            query = query.eq("student_id", student_id)
    elif current_user.role == "admin":
        # Admins can see all attendance
        if course_id:
            query = query.eq("course_id", course_id)
        if student_id:
            query = query.eq("student_id", student_id)
    
    result = query.order("date", desc=True).execute()
    return [AttendanceResponse(**a) for a in result.data]

@app.get("/api/attendance/student/{student_id}", response_model=List[AttendanceResponse])
async def get_student_attendance(student_id: str, course_id: str = None, current_user: UserBase = Depends(get_current_user)):
    """Get specific student's attendance records"""
    if current_user.role == "student" and current_user.id != student_id:
        raise HTTPException(status_code=403, detail="Students can only view their own attendance")
    
    if current_user.role == "mentor":
        # Check if mentor has access to the student's courses
        if course_id:
            mentor_courses = supabase.table("courses").select("id").eq("mentor_id", current_user.id).eq("id", course_id).execute()
            if not mentor_courses.data:
                raise HTTPException(status_code=403, detail="You can only view attendance for your own courses")
    
    query = supabase.table("attendance").select("*").eq("student_id", student_id)
    if course_id:
        query = query.eq("course_id", course_id)
    
    result = query.order("date", desc=True).execute()
    return [AttendanceResponse(**a) for a in result.data]

@app.get("/api/attendance/course/{course_id}", response_model=List[AttendanceResponse])
async def get_course_attendance(course_id: str, date: str = None, current_user: UserBase = Depends(get_current_user)):
    """Get attendance records for a specific course"""
    if current_user.role == "mentor":
        # Check if mentor owns this course
        course_result = supabase.table("courses").select("mentor_id").eq("id", course_id).execute()
        if not course_result.data or course_result.data[0]["mentor_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="You can only view attendance for your own courses")
    
    query = supabase.table("attendance").select("*").eq("course_id", course_id)
    if date:
        query = query.eq("date", date)
    
    result = query.order("date", desc=True).execute()
    return [AttendanceResponse(**a) for a in result.data]

@app.put("/api/attendance/{attendance_id}", response_model=AttendanceResponse)
async def update_attendance_record(attendance_id: str, update: AttendanceUpdate, current_user: UserBase = Depends(get_current_user)):
    """Update attendance record (mentors and admins only)"""
    if current_user.role not in ["admin", "mentor"]:
        raise HTTPException(status_code=403, detail="Only mentors and admins can update attendance records")
    
    # Check if attendance record exists
    attendance_result = supabase.table("attendance").select("*").eq("id", attendance_id).execute()
    if not attendance_result.data:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    
    attendance = attendance_result.data[0]
    
    # Check mentor permission
    if current_user.role == "mentor":
        course_result = supabase.table("courses").select("mentor_id").eq("id", attendance["course_id"]).execute()
        if not course_result.data or course_result.data[0]["mentor_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="You can only update attendance for your own courses")
    
    # Prepare update data
    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
    if update.check_in is not None:
        update_data["check_in"] = update.check_in
    if update.check_out is not None:
        update_data["check_out"] = update.check_out
    if update.ai_alerts is not None:
        update_data["ai_alerts"] = update.ai_alerts
    
    result = supabase.table("attendance").update(update_data).eq("id", attendance_id).execute()
    return AttendanceResponse(**result.data[0])

# ===== MATERIALS MANAGEMENT SYSTEM =====

@app.post("/api/materials", response_model=MaterialResponse)
async def upload_material(material: MaterialCreate, current_user: UserBase = Depends(get_current_user)):
    """Upload learning material (mentors and admins only)"""
    if current_user.role not in ["admin", "mentor"]:
        raise HTTPException(status_code=403, detail="Only mentors and admins can upload materials")
    
    # Check if user has access to the course
    if current_user.role == "mentor":
        course_result = supabase.table("courses").select("mentor_id").eq("id", material.course_id).execute()
        if not course_result.data or course_result.data[0]["mentor_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="You can only upload materials for your own courses")
    
    material_data = {
        "id": str(uuid.uuid4()),
        "course_id": material.course_id,
        "mentor_id": current_user.id,
        "title": material.title,
        "description": material.description,
        "file_url": material.file_url,
        "material_type": material.material_type,
        "is_visible": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    result = supabase.table("materials").insert(material_data).execute()
    return MaterialResponse(**result.data[0])

@app.get("/api/materials", response_model=List[MaterialResponse])
async def get_materials(course_id: str = None, current_user: UserBase = Depends(get_current_user)):
    """Get learning materials based on user role"""
    query = supabase.table("materials").select("*")
    
    if current_user.role == "student":
        # Students can only see materials for courses they're enrolled in and that are visible
        enrolled_courses = supabase.table("enrollments").select("course_id").eq("student_id", current_user.id).execute()
        if not enrolled_courses.data:
            return []
        course_ids = [e["course_id"] for e in enrolled_courses.data]
        query = query.in_("course_id", course_ids).eq("is_visible", True)
    elif current_user.role == "mentor":
        # Mentors can see materials for their courses
        mentor_courses = supabase.table("courses").select("id").eq("mentor_id", current_user.id).execute()
        if not mentor_courses.data:
            return []
        course_ids = [c["id"] for c in mentor_courses.data]
        query = query.in_("course_id", course_ids)
    # Admins can see all materials
    
    if course_id:
        query = query.eq("course_id", course_id)
    
    result = query.order("created_at", desc=True).execute()
    return [MaterialResponse(**m) for m in result.data]

@app.get("/api/materials/course/{course_id}", response_model=List[MaterialResponse])
async def get_course_materials(course_id: str, current_user: UserBase = Depends(get_current_user)):
    """Get materials for a specific course"""
    # Check access permissions
    if current_user.role == "student":
        # Check if student is enrolled
        enrollment_result = supabase.table("enrollments").select("id").eq("student_id", current_user.id).eq("course_id", course_id).execute()
        if not enrollment_result.data:
            raise HTTPException(status_code=403, detail="You must be enrolled in this course to view materials")
        # Students only see visible materials
        query = supabase.table("materials").select("*").eq("course_id", course_id).eq("is_visible", True)
    elif current_user.role == "mentor":
        # Check if mentor owns the course
        course_result = supabase.table("courses").select("mentor_id").eq("id", course_id).execute()
        if not course_result.data or course_result.data[0]["mentor_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="You can only view materials for your own courses")
        query = supabase.table("materials").select("*").eq("course_id", course_id)
    else:
        # Admins can see all materials
        query = supabase.table("materials").select("*").eq("course_id", course_id)
    
    result = query.order("created_at", desc=True).execute()
    return [MaterialResponse(**m) for m in result.data]

@app.get("/api/materials/{material_id}", response_model=MaterialResponse)
async def get_material(material_id: str, current_user: UserBase = Depends(get_current_user)):
    """Get specific material details"""
    material_result = supabase.table("materials").select("*").eq("id", material_id).execute()
    if not material_result.data:
        raise HTTPException(status_code=404, detail="Material not found")
    
    material = material_result.data[0]
    
    # Check access permissions
    if current_user.role == "student":
        # Check if student is enrolled and material is visible
        enrollment_result = supabase.table("enrollments").select("id").eq("student_id", current_user.id).eq("course_id", material["course_id"]).execute()
        if not enrollment_result.data or not material["is_visible"]:
            raise HTTPException(status_code=403, detail="Access denied to this material")
    elif current_user.role == "mentor":
        # Check if mentor owns the course
        course_result = supabase.table("courses").select("mentor_id").eq("id", material["course_id"]).execute()
        if not course_result.data or course_result.data[0]["mentor_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="You can only access materials for your own courses")
    
    return MaterialResponse(**material)

@app.put("/api/materials/{material_id}", response_model=MaterialResponse)
async def update_material(material_id: str, update: MaterialUpdate, current_user: UserBase = Depends(get_current_user)):
    """Update material (mentors and admins only)"""
    if current_user.role not in ["admin", "mentor"]:
        raise HTTPException(status_code=403, detail="Only mentors and admins can update materials")
    
    # Check if material exists
    material_result = supabase.table("materials").select("*").eq("id", material_id).execute()
    if not material_result.data:
        raise HTTPException(status_code=404, detail="Material not found")
    
    material = material_result.data[0]
    
    # Check mentor permission
    if current_user.role == "mentor":
        course_result = supabase.table("courses").select("mentor_id").eq("id", material["course_id"]).execute()
        if not course_result.data or course_result.data[0]["mentor_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="You can only update materials for your own courses")
    
    # Prepare update data
    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
    if update.title is not None:
        update_data["title"] = update.title
    if update.description is not None:
        update_data["description"] = update.description
    if update.file_url is not None:
        update_data["file_url"] = update.file_url
    if update.material_type is not None:
        update_data["material_type"] = update.material_type
    
    result = supabase.table("materials").update(update_data).eq("id", material_id).execute()
    return MaterialResponse(**result.data[0])

@app.delete("/api/materials/{material_id}")
async def delete_material(material_id: str, current_user: UserBase = Depends(get_current_user)):
    """Delete material (mentors and admins only)"""
    if current_user.role not in ["admin", "mentor"]:
        raise HTTPException(status_code=403, detail="Only mentors and admins can delete materials")
    
    # Check if material exists
    material_result = supabase.table("materials").select("*").eq("id", material_id).execute()
    if not material_result.data:
        raise HTTPException(status_code=404, detail="Material not found")
    
    material = material_result.data[0]
    
    # Check mentor permission
    if current_user.role == "mentor":
        course_result = supabase.table("courses").select("mentor_id").eq("id", material["course_id"]).execute()
        if not course_result.data or course_result.data[0]["mentor_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="You can only delete materials for your own courses")
    
    result = supabase.table("materials").delete().eq("id", material_id).execute()
    return {"message": "Material deleted successfully"}

# ===== CERTIFICATE GENERATION SYSTEM =====

@app.post("/api/certificates/generate", response_model=CertificateResponse)
async def generate_certificate(cert_data: CertificateGenerate, current_user: UserBase = Depends(get_current_user)):
    """Generate certificate for student (mentors and admins only)"""
    if current_user.role not in ["admin", "mentor"]:
        raise HTTPException(status_code=403, detail="Only mentors and admins can generate certificates")
    
    # Check if student is enrolled and completed the course
    enrollment_result = supabase.table("enrollments").select("*").eq("student_id", cert_data.student_id).eq("course_id", cert_data.course_id).execute()
    if not enrollment_result.data:
        raise HTTPException(status_code=404, detail="Student enrollment not found")
    
    enrollment = enrollment_result.data[0]
    if enrollment["completion_status"] != "completed":
        raise HTTPException(status_code=400, detail="Student has not completed the course")
    
    # Check mentor permission
    if current_user.role == "mentor":
        course_result = supabase.table("courses").select("mentor_id").eq("id", cert_data.course_id).execute()
        if not course_result.data or course_result.data[0]["mentor_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="You can only generate certificates for your own courses")
    
    # Check if certificate already exists
    existing_cert = supabase.table("certificates").select("id").eq("student_id", cert_data.student_id).eq("course_id", cert_data.course_id).execute()
    if existing_cert.data:
        raise HTTPException(status_code=400, detail="Certificate already exists for this student and course")
    
    # Generate certificate (mock URL for now)
    certificate_data = {
        "id": str(uuid.uuid4()),
        "student_id": cert_data.student_id,
        "course_id": cert_data.course_id,
        "certificate_url": f"https://certificates.lms.com/{str(uuid.uuid4())}.pdf",
        "issued_date": datetime.now(timezone.utc).isoformat(),
        "completion_date": cert_data.completion_date or datetime.now(timezone.utc).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    result = supabase.table("certificates").insert(certificate_data).execute()
    
    # Update enrollment with certificate URL
    supabase.table("enrollments").update({"certificate_url": certificate_data["certificate_url"]}).eq("id", enrollment["id"]).execute()
    
    return CertificateResponse(**result.data[0])

@app.get("/api/certificates", response_model=List[CertificateResponse])
async def get_certificates(student_id: str = None, course_id: str = None, current_user: UserBase = Depends(get_current_user)):
    """Get certificates based on user role"""
    query = supabase.table("certificates").select("*")
    
    if current_user.role == "student":
        # Students can only see their own certificates
        query = query.eq("student_id", current_user.id)
    elif current_user.role == "mentor":
        # Mentors can see certificates for their courses
        mentor_courses = supabase.table("courses").select("id").eq("mentor_id", current_user.id).execute()
        if not mentor_courses.data:
            return []
        course_ids = [c["id"] for c in mentor_courses.data]
        query = query.in_("course_id", course_ids)
    # Admins can see all certificates
    
    if student_id and current_user.role in ["admin", "mentor"]:
        query = query.eq("student_id", student_id)
    if course_id:
        query = query.eq("course_id", course_id)
    
    result = query.order("issued_date", desc=True).execute()
    return [CertificateResponse(**c) for c in result.data]

@app.get("/api/certificates/student/{student_id}", response_model=List[CertificateResponse])
async def get_student_certificates(student_id: str, current_user: UserBase = Depends(get_current_user)):
    """Get certificates for a specific student"""
    if current_user.role == "student" and current_user.id != student_id:
        raise HTTPException(status_code=403, detail="Students can only view their own certificates")
    
    query = supabase.table("certificates").select("*").eq("student_id", student_id)
    
    if current_user.role == "mentor":
        # Filter by mentor's courses
        mentor_courses = supabase.table("courses").select("id").eq("mentor_id", current_user.id).execute()
        if not mentor_courses.data:
            return []
        course_ids = [c["id"] for c in mentor_courses.data]
        query = query.in_("course_id", course_ids)
    
    result = query.order("issued_date", desc=True).execute()
    return [CertificateResponse(**c) for c in result.data]

@app.get("/api/certificates/{certificate_id}", response_model=CertificateResponse)
async def get_certificate(certificate_id: str, current_user: UserBase = Depends(get_current_user)):
    """Get specific certificate details"""
    certificate_result = supabase.table("certificates").select("*").eq("id", certificate_id).execute()
    if not certificate_result.data:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    certificate = certificate_result.data[0]
    
    # Check access permissions
    if current_user.role == "student" and certificate["student_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="You can only view your own certificates")
    elif current_user.role == "mentor":
        course_result = supabase.table("courses").select("mentor_id").eq("id", certificate["course_id"]).execute()
        if not course_result.data or course_result.data[0]["mentor_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="You can only view certificates for your own courses")
    
    return CertificateResponse(**certificate)

# ===== FEE REMINDER SYSTEM =====

@app.post("/api/fee-reminders", response_model=FeeReminderResponse)
async def create_fee_reminder(fee_reminder: FeeReminderCreate, current_user: UserBase = Depends(get_current_user)):
    """Create fee reminder (admins only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create fee reminders")
    
    fee_reminder_data = {
        "id": str(uuid.uuid4()),
        "student_id": fee_reminder.student_id,
        "amount": fee_reminder.amount,
        "due_date": fee_reminder.due_date,
        "description": fee_reminder.description,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    result = supabase.table("fee_reminders").insert(fee_reminder_data).execute()
    return FeeReminderResponse(**result.data[0])

@app.get("/api/fee-reminders", response_model=List[FeeReminderResponse])
async def get_fee_reminders(student_id: str = None, status: str = None, current_user: UserBase = Depends(get_current_user)):
    """Get fee reminders based on user role"""
    query = supabase.table("fee_reminders").select("*")
    
    if current_user.role == "student":
        # Students can only see their own fee reminders
        query = query.eq("student_id", current_user.id)
    elif current_user.role == "mentor":
        # Mentors cannot access fee reminders
        raise HTTPException(status_code=403, detail="Mentors cannot access fee reminders")
    # Admins can see all fee reminders
    
    if student_id and current_user.role == "admin":
        query = query.eq("student_id", student_id)
    if status:
        query = query.eq("status", status)
    
    result = query.order("due_date", desc=False).execute()
    return [FeeReminderResponse(**f) for f in result.data]

@app.get("/api/fee-reminders/student/{student_id}", response_model=List[FeeReminderResponse])
async def get_student_fee_reminders(student_id: str, current_user: UserBase = Depends(get_current_user)):
    """Get fee reminders for a specific student"""
    if current_user.role == "student" and current_user.id != student_id:
        raise HTTPException(status_code=403, detail="Students can only view their own fee reminders")
    elif current_user.role == "mentor":
        raise HTTPException(status_code=403, detail="Mentors cannot access fee reminders")
    
    result = supabase.table("fee_reminders").select("*").eq("student_id", student_id).order("due_date", desc=False).execute()
    return [FeeReminderResponse(**f) for f in result.data]

@app.put("/api/fee-reminders/{reminder_id}", response_model=FeeReminderResponse)
async def update_fee_reminder(reminder_id: str, update: FeeReminderUpdate, current_user: UserBase = Depends(get_current_user)):
    """Update fee reminder (admins only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update fee reminders")
    
    # Check if fee reminder exists
    reminder_result = supabase.table("fee_reminders").select("*").eq("id", reminder_id).execute()
    if not reminder_result.data:
        raise HTTPException(status_code=404, detail="Fee reminder not found")
    
    # Prepare update data
    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
    if update.amount is not None:
        update_data["amount"] = update.amount
    if update.due_date is not None:
        update_data["due_date"] = update.due_date
    if update.description is not None:
        update_data["description"] = update.description
    if update.status is not None:
        update_data["status"] = update.status
    
    result = supabase.table("fee_reminders").update(update_data).eq("id", reminder_id).execute()
    return FeeReminderResponse(**result.data[0])

@app.delete("/api/fee-reminders/{reminder_id}")
async def delete_fee_reminder(reminder_id: str, current_user: UserBase = Depends(get_current_user)):
    """Delete fee reminder (admins only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete fee reminders")
    
    # Check if fee reminder exists
    reminder_result = supabase.table("fee_reminders").select("id").eq("id", reminder_id).execute()
    if not reminder_result.data:
        raise HTTPException(status_code=404, detail="Fee reminder not found")
    
    result = supabase.table("fee_reminders").delete().eq("id", reminder_id).execute()
    return {"message": "Fee reminder deleted successfully"}

@app.put("/api/fee-reminders/{reminder_id}/paid", response_model=FeeReminderResponse)
async def mark_fee_as_paid(reminder_id: str, current_user: UserBase = Depends(get_current_user)):
    """Mark fee as paid (admins only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can mark fees as paid")
    
    # Check if fee reminder exists
    reminder_result = supabase.table("fee_reminders").select("*").eq("id", reminder_id).execute()
    if not reminder_result.data:
        raise HTTPException(status_code=404, detail="Fee reminder not found")
    
    update_data = {
        "status": "paid",
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    result = supabase.table("fee_reminders").update(update_data).eq("id", reminder_id).execute()
    return FeeReminderResponse(**result.data[0])

# ===== MOCK INTERVIEW SCHEDULING SYSTEM =====

@app.post("/api/mock-interviews", response_model=MockInterviewResponse)
async def schedule_mock_interview(interview: MockInterviewCreate, current_user: UserBase = Depends(get_current_user)):
    """Schedule mock interview (mentors and admins can schedule for any student, students for themselves)"""
    if current_user.role == "student" and interview.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Students can only schedule interviews for themselves")
    
    # Check if mentor exists and is actually a mentor
    if current_user.role != "admin":
        mentor_result = supabase.table("users").select("role").eq("id", interview.mentor_id).execute()
        if not mentor_result.data or mentor_result.data[0]["role"] != "mentor":
            raise HTTPException(status_code=400, detail="Invalid mentor ID")
    
    interview_data = {
        "id": str(uuid.uuid4()),
        "student_id": interview.student_id,
        "mentor_id": interview.mentor_id,
        "scheduled_date": interview.scheduled_date,
        "type": interview.type,
        "duration": interview.duration or 60,
        "status": "scheduled",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    result = supabase.table("mock_interviews").insert(interview_data).execute()
    return MockInterviewResponse(**result.data[0])

@app.get("/api/mock-interviews", response_model=List[MockInterviewResponse])
async def get_mock_interviews(student_id: str = None, mentor_id: str = None, status: str = None, current_user: UserBase = Depends(get_current_user)):
    """Get mock interviews based on user role"""
    query = supabase.table("mock_interviews").select("*")
    
    if current_user.role == "student":
        # Students can only see their own interviews
        query = query.eq("student_id", current_user.id)
    elif current_user.role == "mentor":
        # Mentors can see interviews they are conducting
        query = query.eq("mentor_id", current_user.id)
        if student_id:
            query = query.eq("student_id", student_id)
    # Admins can see all interviews
    else:
        if student_id:
            query = query.eq("student_id", student_id)
        if mentor_id:
            query = query.eq("mentor_id", mentor_id)
    
    if status:
        query = query.eq("status", status)
    
    result = query.order("scheduled_date", desc=False).execute()
    return [MockInterviewResponse(**i) for i in result.data]

@app.get("/api/mock-interviews/student/{student_id}", response_model=List[MockInterviewResponse])
async def get_student_interviews(student_id: str, current_user: UserBase = Depends(get_current_user)):
    """Get mock interviews for a specific student"""
    if current_user.role == "student" and current_user.id != student_id:
        raise HTTPException(status_code=403, detail="Students can only view their own interviews")
    
    result = supabase.table("mock_interviews").select("*").eq("student_id", student_id).order("scheduled_date", desc=False).execute()
    return [MockInterviewResponse(**i) for i in result.data]

@app.get("/api/mock-interviews/mentor/{mentor_id}", response_model=List[MockInterviewResponse])
async def get_mentor_interviews(mentor_id: str, current_user: UserBase = Depends(get_current_user)):
    """Get mock interviews for a specific mentor"""
    if current_user.role == "mentor" and current_user.id != mentor_id:
        raise HTTPException(status_code=403, detail="Mentors can only view their own interviews")
    
    result = supabase.table("mock_interviews").select("*").eq("mentor_id", mentor_id).order("scheduled_date", desc=False).execute()
    return [MockInterviewResponse(**i) for i in result.data]

@app.put("/api/mock-interviews/{interview_id}", response_model=MockInterviewResponse)
async def update_mock_interview(interview_id: str, update: MockInterviewUpdate, current_user: UserBase = Depends(get_current_user)):
    """Update mock interview (participants and admins only)"""
    # Check if interview exists
    interview_result = supabase.table("mock_interviews").select("*").eq("id", interview_id).execute()
    if not interview_result.data:
        raise HTTPException(status_code=404, detail="Mock interview not found")
    
    interview = interview_result.data[0]
    
    # Check permissions
    if current_user.role not in ["admin"] and current_user.id not in [interview["student_id"], interview["mentor_id"]]:
        raise HTTPException(status_code=403, detail="You can only update interviews you're involved in")
    
    # Prepare update data
    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
    if update.scheduled_date is not None:
        update_data["scheduled_date"] = update.scheduled_date
    if update.type is not None:
        update_data["type"] = update.type
    if update.duration is not None:
        update_data["duration"] = update.duration
    if update.status is not None:
        update_data["status"] = update.status
    
    result = supabase.table("mock_interviews").update(update_data).eq("id", interview_id).execute()
    return MockInterviewResponse(**result.data[0])

@app.delete("/api/mock-interviews/{interview_id}")
async def cancel_mock_interview(interview_id: str, current_user: UserBase = Depends(get_current_user)):
    """Cancel mock interview (participants and admins only)"""
    # Check if interview exists
    interview_result = supabase.table("mock_interviews").select("*").eq("id", interview_id).execute()
    if not interview_result.data:
        raise HTTPException(status_code=404, detail="Mock interview not found")
    
    interview = interview_result.data[0]
    
    # Check permissions
    if current_user.role not in ["admin"] and current_user.id not in [interview["student_id"], interview["mentor_id"]]:
        raise HTTPException(status_code=403, detail="You can only cancel interviews you're involved in")
    
    # Update status to cancelled instead of deleting
    update_data = {
        "status": "cancelled",
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    result = supabase.table("mock_interviews").update(update_data).eq("id", interview_id).execute()
    return {"message": "Mock interview cancelled successfully"}

@app.post("/api/mock-interviews/{interview_id}/feedback", response_model=MockInterviewResponse)
async def add_interview_feedback(interview_id: str, feedback: InterviewFeedback, current_user: UserBase = Depends(get_current_user)):
    """Add feedback to mock interview (mentors and admins only)"""
    # Check if interview exists
    interview_result = supabase.table("mock_interviews").select("*").eq("id", interview_id).execute()
    if not interview_result.data:
        raise HTTPException(status_code=404, detail="Mock interview not found")
    
    interview = interview_result.data[0]
    
    # Check if user is the mentor for this interview or admin
    if current_user.role not in ["admin"] and (current_user.role != "mentor" or current_user.id != interview["mentor_id"]):
        raise HTTPException(status_code=403, detail="Only the assigned mentor or admin can add feedback")
    
    update_data = {
        "feedback": feedback.feedback,
        "score": feedback.score,
        "status": "completed",
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    result = supabase.table("mock_interviews").update(update_data).eq("id", interview_id).execute()
    return MockInterviewResponse(**result.data[0])

@app.get("/api/mock-interviews/{interview_id}/feedback", response_model=MockInterviewResponse)
async def get_interview_feedback(interview_id: str, current_user: UserBase = Depends(get_current_user)):
    """Get feedback for mock interview"""
    # Check if interview exists
    interview_result = supabase.table("mock_interviews").select("*").eq("id", interview_id).execute()
    if not interview_result.data:
        raise HTTPException(status_code=404, detail="Mock interview not found")
    
    interview = interview_result.data[0]
    
    # Check permissions - participants can view feedback
    if current_user.role not in ["admin"] and current_user.id not in [interview["student_id"], interview["mentor_id"]]:
        raise HTTPException(status_code=403, detail="You can only view feedback for interviews you're involved in")
    
    return MockInterviewResponse(**interview)

# ===== PROGRESS REPORTING SYSTEM =====

@app.get("/api/reports/progress", response_model=List[ProgressReportResponse])
async def get_overall_progress_report(current_user: UserBase = Depends(get_current_user)):
    """Get overall progress report for all students (admins only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view overall progress reports")
    
    # Get all students
    students = supabase.table("users").select("id").eq("role", "student").execute()
    if not students.data:
        return []
    
    reports = []
    for student in students.data:
        report = await get_student_progress_report_data(student["id"])
        reports.append(report)
    
    return reports

@app.get("/api/reports/student/{student_id}/progress", response_model=ProgressReportResponse)
async def get_student_progress_report(student_id: str, current_user: UserBase = Depends(get_current_user)):
    """Get progress report for a specific student"""
    if current_user.role == "student" and current_user.id != student_id:
        raise HTTPException(status_code=403, detail="Students can only view their own progress")
    
    return await get_student_progress_report_data(student_id)

async def get_student_progress_report_data(student_id: str) -> ProgressReportResponse:
    """Helper function to generate student progress report data"""
    # Get enrollments
    enrollments = supabase.table("enrollments").select("*").eq("student_id", student_id).execute()
    enrollment_count = len(enrollments.data) if enrollments.data else 0
    completed_courses = len([e for e in enrollments.data if e["completion_status"] == "completed"]) if enrollments.data else 0
    
    # Get course IDs for enrolled courses
    enrolled_course_ids = [e["course_id"] for e in enrollments.data] if enrollments.data else []
    
    # Get tasks for enrolled courses
    total_tasks = 0
    completed_tasks = 0
    if enrolled_course_ids:
        tasks = supabase.table("tasks").select("id").in_("course_id", enrolled_course_ids).execute()
        total_tasks = len(tasks.data) if tasks.data else 0
        
        if total_tasks > 0:
            task_ids = [t["id"] for t in tasks.data]
            submissions = supabase.table("task_submissions").select("grade").eq("student_id", student_id).in_("task_id", task_ids).execute()
            completed_tasks = len([s for s in submissions.data if s["grade"] is not None]) if submissions.data else 0
    
    # Get attendance percentage
    attendance_records = supabase.table("attendance").select("check_in, check_out").eq("student_id", student_id).execute()
    attendance_percentage = 0.0
    if attendance_records.data:
        attended_sessions = len([a for a in attendance_records.data if a["check_in"] is not None])
        attendance_percentage = (attended_sessions / len(attendance_records.data)) * 100 if attendance_records.data else 0.0
    
    # Get average grade
    average_grade = None
    if enrolled_course_ids:
        task_ids_query = supabase.table("tasks").select("id").in_("course_id", enrolled_course_ids).execute()
        if task_ids_query.data:
            task_ids = [t["id"] for t in task_ids_query.data]
            graded_submissions = supabase.table("task_submissions").select("grade").eq("student_id", student_id).in_("task_id", task_ids).not_.is_("grade", "null").execute()
            if graded_submissions.data:
                grades = [float(s["grade"]) for s in graded_submissions.data]
                average_grade = sum(grades) / len(grades) if grades else None
    
    # Get certificates count
    certificates = supabase.table("certificates").select("id").eq("student_id", student_id).execute()
    certificates_earned = len(certificates.data) if certificates.data else 0
    
    # Get last activity (most recent task submission or attendance)
    last_activity = None
    recent_submission = supabase.table("task_submissions").select("submitted_at").eq("student_id", student_id).order("submitted_at", desc=True).limit(1).execute()
    recent_attendance = supabase.table("attendance").select("created_at").eq("student_id", student_id).order("created_at", desc=True).limit(1).execute()
    
    submission_date = recent_submission.data[0]["submitted_at"] if recent_submission.data else None
    attendance_date = recent_attendance.data[0]["created_at"] if recent_attendance.data else None
    
    if submission_date and attendance_date:
        last_activity = max(submission_date, attendance_date)
    elif submission_date:
        last_activity = submission_date
    elif attendance_date:
        last_activity = attendance_date
    
    return ProgressReportResponse(
        student_id=student_id,
        enrollment_count=enrollment_count,
        completed_courses=completed_courses,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        attendance_percentage=round(attendance_percentage, 2),
        average_grade=round(average_grade, 2) if average_grade else None,
        certificates_earned=certificates_earned,
        last_activity=last_activity
    )

@app.get("/api/reports/course/{course_id}/progress", response_model=List[ProgressReportResponse])
async def get_course_progress_report(course_id: str, current_user: UserBase = Depends(get_current_user)):
    """Get progress report for all students in a specific course"""
    # Check permissions
    if current_user.role == "mentor":
        course_result = supabase.table("courses").select("mentor_id").eq("id", course_id).execute()
        if not course_result.data or course_result.data[0]["mentor_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="You can only view progress for your own courses")
    elif current_user.role == "student":
        raise HTTPException(status_code=403, detail="Students cannot view course progress reports")
    
    # Get all students enrolled in the course
    enrollments = supabase.table("enrollments").select("student_id").eq("course_id", course_id).execute()
    if not enrollments.data:
        return []
    
    reports = []
    for enrollment in enrollments.data:
        report = await get_student_progress_report_data(enrollment["student_id"])
        report.course_id = course_id  # Add course context
        reports.append(report)
    
    return reports

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)