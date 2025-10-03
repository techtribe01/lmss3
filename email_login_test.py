#!/usr/bin/env python3
"""
Test email login functionality specifically
"""

import requests
import json
import time

BACKEND_URL = "https://securelearn-4.preview.emergentagent.com/api"

def test_email_login():
    """Test that users can login with email instead of username"""
    print("🔍 Testing Email Login Functionality...")
    
    # Generate unique user for this test
    timestamp = str(int(time.time()))
    username = f"email_test_user_{timestamp}"
    email = f"email_test_{timestamp}@test.com"
    password = "testpass123"
    
    # First register a user
    register_data = {
        "username": username,
        "email": email,
        "password": password,
        "full_name": "Email Test User",
        "role": "student"
    }
    
    register_response = requests.post(f"{BACKEND_URL}/auth/register", json=register_data)
    if register_response.status_code != 200:
        print(f"❌ Registration failed: {register_response.text}")
        return False
    
    print("✅ User registered successfully")
    
    # Test 1: Login with username (should work)
    login_data = {
        "username": username,
        "password": password
    }
    
    login_response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
    if login_response.status_code != 200:
        print(f"❌ Username login failed: {login_response.text}")
        return False
    
    print("✅ Username login successful")
    
    # Test 2: Login with email (should also work)
    login_data = {
        "username": email,  # Using email in username field
        "password": password
    }
    
    login_response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
    if login_response.status_code != 200:
        print(f"❌ Email login failed: {login_response.text}")
        return False
    
    login_data = login_response.json()
    if "access_token" in login_data and "user" in login_data:
        user_data = login_data["user"]
        if user_data["email"] == email:
            print("✅ Email login successful - user can login with email address")
            return True
        else:
            print(f"❌ Email mismatch in response: expected {email}, got {user_data.get('email')}")
            return False
    else:
        print(f"❌ Invalid login response format: {login_data}")
        return False

if __name__ == "__main__":
    success = test_email_login()
    if success:
        print("\n🎉 Email login functionality is working correctly!")
    else:
        print("\n❌ Email login functionality has issues.")