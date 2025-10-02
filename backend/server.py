from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, List
import os
from datetime import datetime, timedelta, timezone
import jwt
import bcrypt
import uuid

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB setup
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client.lms_database

# JWT Configuration
SECRET_KEY = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

security = HTTPBearer()

# Pydantic Models
class UserBase(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
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
    user = await db.users.find_one({"id": user_id})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return UserBase(**user)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# Routes
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "LMS Backend"}

@app.post("/api/auth/register", response_model=Token)
async def register(user: UserCreate):
    # Check if username exists
    existing_user = await db.users.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check if email exists
    existing_email = await db.users.find_one({"email": user.email})
    if existing_email:
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
        "password": hashed_pwd,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(new_user)
    
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
    # Try to find user by username or email
    user = await db.users.find_one({
        "$or": [
            {"username": credentials.username},
            {"email": credentials.username}
        ]
    })
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username/email or password")
    
    if not verify_password(credentials.password, user["password"]):
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
    
    users = await db.users.find().to_list(length=None)
    return [UserResponse(
        id=u["id"],
        username=u["username"],
        email=u["email"],
        full_name=u["full_name"],
        role=u["role"]
    ) for u in users]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)