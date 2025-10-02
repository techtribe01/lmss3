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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)