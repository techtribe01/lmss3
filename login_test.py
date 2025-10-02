#!/usr/bin/env python3
"""
Test script for updated login functionality that accepts username OR email
"""

import requests
import json
import sys
import time

# Backend URL
BACKEND_URL = "https://lms-final-verify.preview.emergentagent.com/api"

def log_test(test_name: str, success: bool, message: str = ""):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if message:
        print(f"   {message}")
    print()

def make_request(method: str, endpoint: str, data: dict = None, headers: dict = None):
    """Make HTTP request and return (success, response, error_message)"""
    url = f"{BACKEND_URL}{endpoint}"
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            return False, None, f"Unsupported method: {method}"
            
        return True, response, None
    except Exception as e:
        return False, None, str(e)

def test_login_with_username_or_email():
    """Test the updated login functionality"""
    print("=" * 60)
    print("🚀 Testing Updated Login Functionality (Username OR Email)")
    print("=" * 60)
    
    # Generate unique test data
    timestamp = str(int(time.time()))
    test_username = f"logintest_{timestamp}"
    test_email = f"logintest_{timestamp}@test.com"
    test_password = "testpass123"
    test_fullname = "Login Test User"
    
    results = []
    
    # Step 1: Create a test user first
    print("🔍 Step 1: Creating test user...")
    user_data = {
        "username": test_username,
        "email": test_email,
        "password": test_password,
        "full_name": test_fullname,
        "role": "student"
    }
    
    success, response, error = make_request("POST", "/auth/register", user_data)
    
    if not success:
        log_test("Create Test User", False, f"Request failed: {error}")
        return False
        
    if response.status_code == 200:
        data = response.json()
        if "access_token" in data and "user" in data:
            log_test("Create Test User", True, f"User created: {test_username} / {test_email}")
        else:
            log_test("Create Test User", False, f"Missing token or user data: {data}")
            return False
    else:
        try:
            error_data = response.json()
            log_test("Create Test User", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
        except:
            log_test("Create Test User", False, f"Status {response.status_code}: {response.text}")
        return False
    
    # Step 2: Test login with username
    print("🔍 Step 2: Testing login with username...")
    login_data = {
        "username": test_username,
        "password": test_password
    }
    
    success, response, error = make_request("POST", "/auth/login", login_data)
    
    if not success:
        log_test("Login with Username", False, f"Request failed: {error}")
        results.append(False)
    elif response.status_code == 200:
        data = response.json()
        if "access_token" in data and "user" in data:
            user_data = data["user"]
            if user_data["username"] == test_username:
                log_test("Login with Username", True, f"Successfully logged in with username: {test_username}")
                results.append(True)
            else:
                log_test("Login with Username", False, f"Username mismatch. Expected: {test_username}, Got: {user_data.get('username')}")
                results.append(False)
        else:
            log_test("Login with Username", False, f"Missing token or user data: {data}")
            results.append(False)
    else:
        try:
            error_data = response.json()
            log_test("Login with Username", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
        except:
            log_test("Login with Username", False, f"Status {response.status_code}: {response.text}")
        results.append(False)
    
    # Step 3: Test login with email
    print("🔍 Step 3: Testing login with email...")
    login_data = {
        "username": test_email,  # Using email in the username field
        "password": test_password
    }
    
    success, response, error = make_request("POST", "/auth/login", login_data)
    
    if not success:
        log_test("Login with Email", False, f"Request failed: {error}")
        results.append(False)
    elif response.status_code == 200:
        data = response.json()
        if "access_token" in data and "user" in data:
            user_data = data["user"]
            if user_data["email"] == test_email:
                log_test("Login with Email", True, f"Successfully logged in with email: {test_email}")
                results.append(True)
            else:
                log_test("Login with Email", False, f"Email mismatch. Expected: {test_email}, Got: {user_data.get('email')}")
                results.append(False)
        else:
            log_test("Login with Email", False, f"Missing token or user data: {data}")
            results.append(False)
    else:
        try:
            error_data = response.json()
            log_test("Login with Email", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
        except:
            log_test("Login with Email", False, f"Status {response.status_code}: {response.text}")
        results.append(False)
    
    # Step 4: Test login with invalid username
    print("🔍 Step 4: Testing login with invalid username...")
    invalid_login_data = {
        "username": "nonexistent_user_12345",
        "password": "wrongpassword"
    }
    
    success, response, error = make_request("POST", "/auth/login", invalid_login_data)
    
    if not success:
        log_test("Login with Invalid Username", False, f"Request failed: {error}")
        results.append(False)
    elif response.status_code == 401:
        try:
            error_data = response.json()
            error_message = error_data.get('detail', '')
            if "username/email" in error_message.lower():
                log_test("Login with Invalid Username", True, f"Correct error message: {error_message}")
                results.append(True)
            else:
                log_test("Login with Invalid Username", False, f"Error message should mention 'username/email': {error_message}")
                results.append(False)
        except:
            log_test("Login with Invalid Username", False, f"Could not parse error response: {response.text}")
            results.append(False)
    else:
        log_test("Login with Invalid Username", False, f"Expected 401, got {response.status_code}")
        results.append(False)
    
    # Step 5: Test login with invalid email
    print("🔍 Step 5: Testing login with invalid email...")
    invalid_email_login_data = {
        "username": "nonexistent@email.com",
        "password": "wrongpassword"
    }
    
    success, response, error = make_request("POST", "/auth/login", invalid_email_login_data)
    
    if not success:
        log_test("Login with Invalid Email", False, f"Request failed: {error}")
        results.append(False)
    elif response.status_code == 401:
        try:
            error_data = response.json()
            error_message = error_data.get('detail', '')
            if "username/email" in error_message.lower():
                log_test("Login with Invalid Email", True, f"Correct error message: {error_message}")
                results.append(True)
            else:
                log_test("Login with Invalid Email", False, f"Error message should mention 'username/email': {error_message}")
                results.append(False)
        except:
            log_test("Login with Invalid Email", False, f"Could not parse error response: {response.text}")
            results.append(False)
    else:
        log_test("Login with Invalid Email", False, f"Expected 401, got {response.status_code}")
        results.append(False)
    
    # Summary
    print("=" * 60)
    print("📊 LOGIN TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All login tests passed! Updated login functionality is working correctly.")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = test_login_with_username_or_email()
    sys.exit(0 if success else 1)