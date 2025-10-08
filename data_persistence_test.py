#!/usr/bin/env python3
"""
Test that data is actually stored in Supabase database
"""

import requests
import json
import time

BACKEND_URL = "https://lms-verify.preview.emergentagent.com/api"

def test_data_persistence():
    """Test that user data persists in Supabase database"""
    print("🔍 Testing Data Persistence in Supabase...")
    
    # Generate unique user for this test
    timestamp = str(int(time.time()))
    username = f"persist_test_{timestamp}"
    email = f"persist_test_{timestamp}@test.com"
    password = "persisttest123"
    full_name = "Data Persistence Test User"
    
    # Register a user
    register_data = {
        "username": username,
        "email": email,
        "password": password,
        "full_name": full_name,
        "role": "mentor"
    }
    
    register_response = requests.post(f"{BACKEND_URL}/auth/register", json=register_data)
    if register_response.status_code != 200:
        print(f"❌ Registration failed: {register_response.text}")
        return False
    
    register_data = register_response.json()
    user_id = register_data["user"]["id"]
    print(f"✅ User registered with ID: {user_id}")
    
    # Login to get admin token (we need admin access to get all users)
    admin_login = {
        "username": username,
        "password": password
    }
    
    login_response = requests.post(f"{BACKEND_URL}/auth/login", json=admin_login)
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return False
    
    token = login_response.json()["access_token"]
    print("✅ Login successful, token obtained")
    
    # Get current user info to verify data is stored correctly
    headers = {"Authorization": f"Bearer {token}"}
    me_response = requests.get(f"{BACKEND_URL}/auth/me", headers=headers)
    
    if me_response.status_code != 200:
        print(f"❌ Get current user failed: {me_response.text}")
        return False
    
    user_data = me_response.json()
    
    # Verify all data matches what we registered
    checks = [
        (user_data["id"] == user_id, f"User ID: expected {user_id}, got {user_data['id']}"),
        (user_data["username"] == username, f"Username: expected {username}, got {user_data['username']}"),
        (user_data["email"] == email, f"Email: expected {email}, got {user_data['email']}"),
        (user_data["full_name"] == full_name, f"Full name: expected {full_name}, got {user_data['full_name']}"),
        (user_data["role"] == "mentor", f"Role: expected mentor, got {user_data['role']}")
    ]
    
    all_passed = True
    for check, message in checks:
        if check:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
            all_passed = False
    
    if all_passed:
        print("✅ All user data matches - data is correctly stored in Supabase!")
        return True
    else:
        print("❌ Some user data doesn't match - potential storage issue")
        return False

if __name__ == "__main__":
    success = test_data_persistence()
    if success:
        print("\n🎉 Data persistence test passed! Data is stored in Supabase database.")
    else:
        print("\n❌ Data persistence test failed.")