#!/usr/bin/env python3
"""
Test password security - verify passwords are hashed
"""

import requests
import json
import time
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

BACKEND_URL = "https://auth-refactor-2.preview.emergentagent.com/api"
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

def test_password_security():
    """Test that passwords are properly hashed in database"""
    print("🔍 Testing Password Security (Hashing)...")
    
    # Initialize Supabase client to check database directly
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    
    # Generate unique user for this test
    timestamp = str(int(time.time()))
    username = f"security_test_{timestamp}"
    email = f"security_test_{timestamp}@test.com"
    password = "plaintext_password_123"
    
    # Register a user
    register_data = {
        "username": username,
        "email": email,
        "password": password,
        "full_name": "Security Test User",
        "role": "student"
    }
    
    register_response = requests.post(f"{BACKEND_URL}/auth/register", json=register_data)
    if register_response.status_code != 200:
        print(f"❌ Registration failed: {register_response.text}")
        return False
    
    user_id = register_response.json()["user"]["id"]
    print(f"✅ User registered with ID: {user_id}")
    
    # Query Supabase directly to check password storage
    try:
        result = supabase.table("users").select("password_hash").eq("id", user_id).execute()
        
        if not result.data or len(result.data) == 0:
            print("❌ User not found in database")
            return False
        
        stored_password_hash = result.data[0]["password_hash"]
        
        # Check that password is hashed (not stored in plain text)
        if stored_password_hash == password:
            print(f"❌ SECURITY ISSUE: Password stored in plain text: {stored_password_hash}")
            return False
        
        # Check that it looks like a bcrypt hash (starts with $2b$)
        if not stored_password_hash.startswith("$2b$"):
            print(f"❌ Password doesn't appear to be bcrypt hashed: {stored_password_hash}")
            return False
        
        # Check that hash is reasonable length (bcrypt hashes are typically 60 chars)
        if len(stored_password_hash) < 50:
            print(f"❌ Password hash seems too short: {len(stored_password_hash)} chars")
            return False
        
        print(f"✅ Password is properly hashed with bcrypt")
        print(f"   Hash length: {len(stored_password_hash)} characters")
        print(f"   Hash prefix: {stored_password_hash[:10]}...")
        
        # Test that login still works with the original password
        login_data = {
            "username": username,
            "password": password
        }
        
        login_response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
        if login_response.status_code != 200:
            print(f"❌ Login failed after registration: {login_response.text}")
            return False
        
        print("✅ Login works correctly with original password")
        
        # Test that login fails with wrong password
        wrong_login_data = {
            "username": username,
            "password": "wrong_password"
        }
        
        wrong_login_response = requests.post(f"{BACKEND_URL}/auth/login", json=wrong_login_data)
        if wrong_login_response.status_code == 200:
            print("❌ Login succeeded with wrong password - security issue!")
            return False
        
        print("✅ Login correctly fails with wrong password")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking database: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_password_security()
    if success:
        print("\n🎉 Password security test passed! Passwords are properly hashed.")
    else:
        print("\n❌ Password security test failed - potential security issue!")