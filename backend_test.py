#!/usr/bin/env python3
"""
LMS Backend API Testing Suite
Tests all authentication and user management endpoints
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

# Get backend URL from frontend .env
BACKEND_URL = "https://edu-navigator-5.preview.emergentagent.com/api"

class LMSAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.tokens = {}  # Store tokens for different users
        self.users = {}   # Store user data
        
    def log_test(self, test_name: str, success: bool, message: str = ""):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if message:
            print(f"   {message}")
        print()
        
    def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> tuple:
        """Make HTTP request and return (success, response, error_message)"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=headers)
            else:
                return False, None, f"Unsupported method: {method}"
                
            return True, response, None
        except Exception as e:
            return False, None, str(e)
    
    def test_health_check(self):
        """Test basic health endpoint"""
        print("🔍 Testing Health Check...")
        success, response, error = self.make_request("GET", "/health")
        
        if not success:
            self.log_test("Health Check", False, f"Request failed: {error}")
            return False
            
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                self.log_test("Health Check", True, "Backend is healthy")
                return True
            else:
                self.log_test("Health Check", False, f"Unexpected response: {data}")
                return False
        else:
            self.log_test("Health Check", False, f"Status code: {response.status_code}")
            return False
    
    def test_register_user(self, role: str, username: str, email: str, full_name: str, password: str) -> bool:
        """Test user registration"""
        print(f"🔍 Testing Registration - {role.title()} User...")
        
        user_data = {
            "username": username,
            "email": email,
            "password": password,
            "full_name": full_name,
            "role": role
        }
        
        success, response, error = self.make_request("POST", "/auth/register", user_data)
        
        if not success:
            self.log_test(f"Register {role.title()}", False, f"Request failed: {error}")
            return False
            
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data and "user" in data:
                # Store token and user data for later tests
                self.tokens[role] = data["access_token"]
                self.users[role] = data["user"]
                self.log_test(f"Register {role.title()}", True, f"User registered successfully. Token received.")
                return True
            else:
                self.log_test(f"Register {role.title()}", False, f"Missing token or user data: {data}")
                return False
        else:
            try:
                error_data = response.json()
                self.log_test(f"Register {role.title()}", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
            except:
                self.log_test(f"Register {role.title()}", False, f"Status {response.status_code}: {response.text}")
            return False
    
    def test_duplicate_registration(self):
        """Test duplicate username/email registration"""
        print("🔍 Testing Duplicate Registration...")
        
        # Try to register with existing username
        duplicate_data = {
            "username": "admin_user",  # This should already exist
            "email": "duplicate@test.com",
            "password": "password123",
            "full_name": "Duplicate User",
            "role": "student"
        }
        
        success, response, error = self.make_request("POST", "/auth/register", duplicate_data)
        
        if not success:
            self.log_test("Duplicate Username", False, f"Request failed: {error}")
            return False
            
        if response.status_code == 400:
            data = response.json()
            if "already exists" in data.get("detail", "").lower():
                self.log_test("Duplicate Username", True, "Correctly rejected duplicate username")
                return True
            else:
                self.log_test("Duplicate Username", False, f"Wrong error message: {data}")
                return False
        else:
            self.log_test("Duplicate Username", False, f"Expected 400, got {response.status_code}")
            return False
    
    def test_login(self, role: str, username: str, password: str) -> bool:
        """Test user login"""
        print(f"🔍 Testing Login - {role.title()} User...")
        
        login_data = {
            "username": username,
            "password": password
        }
        
        success, response, error = self.make_request("POST", "/auth/login", login_data)
        
        if not success:
            self.log_test(f"Login {role.title()}", False, f"Request failed: {error}")
            return False
            
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data and "user" in data:
                # Update token (in case it's different from registration)
                self.tokens[role] = data["access_token"]
                user_data = data["user"]
                if user_data["role"] == role:
                    self.log_test(f"Login {role.title()}", True, f"Login successful. Role: {user_data['role']}")
                    return True
                else:
                    self.log_test(f"Login {role.title()}", False, f"Role mismatch. Expected: {role}, Got: {user_data['role']}")
                    return False
            else:
                self.log_test(f"Login {role.title()}", False, f"Missing token or user data: {data}")
                return False
        else:
            try:
                error_data = response.json()
                self.log_test(f"Login {role.title()}", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
            except:
                self.log_test(f"Login {role.title()}", False, f"Status {response.status_code}: {response.text}")
            return False
    
    def test_invalid_login(self):
        """Test login with invalid credentials"""
        print("🔍 Testing Invalid Login...")
        
        invalid_data = {
            "username": "nonexistent_user",
            "password": "wrong_password"
        }
        
        success, response, error = self.make_request("POST", "/auth/login", invalid_data)
        
        if not success:
            self.log_test("Invalid Login", False, f"Request failed: {error}")
            return False
            
        if response.status_code == 401:
            self.log_test("Invalid Login", True, "Correctly rejected invalid credentials")
            return True
        else:
            self.log_test("Invalid Login", False, f"Expected 401, got {response.status_code}")
            return False
    
    def test_get_current_user(self, role: str) -> bool:
        """Test getting current user info"""
        print(f"🔍 Testing Get Current User - {role.title()}...")
        
        if role not in self.tokens:
            self.log_test(f"Get Current User {role.title()}", False, f"No token available for {role}")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        success, response, error = self.make_request("GET", "/auth/me", headers=headers)
        
        if not success:
            self.log_test(f"Get Current User {role.title()}", False, f"Request failed: {error}")
            return False
            
        if response.status_code == 200:
            data = response.json()
            if data.get("role") == role:
                self.log_test(f"Get Current User {role.title()}", True, f"Retrieved user info. Role: {data['role']}")
                return True
            else:
                self.log_test(f"Get Current User {role.title()}", False, f"Role mismatch. Expected: {role}, Got: {data.get('role')}")
                return False
        else:
            try:
                error_data = response.json()
                self.log_test(f"Get Current User {role.title()}", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
            except:
                self.log_test(f"Get Current User {role.title()}", False, f"Status {response.status_code}: {response.text}")
            return False
    
    def test_get_current_user_no_token(self):
        """Test getting current user without token"""
        print("🔍 Testing Get Current User - No Token...")
        
        success, response, error = self.make_request("GET", "/auth/me")
        
        if not success:
            self.log_test("Get Current User No Token", False, f"Request failed: {error}")
            return False
            
        if response.status_code == 403:  # FastAPI HTTPBearer returns 403 for missing token
            self.log_test("Get Current User No Token", True, "Correctly rejected request without token")
            return True
        else:
            self.log_test("Get Current User No Token", False, f"Expected 403, got {response.status_code}")
            return False
    
    def test_get_all_users_admin(self) -> bool:
        """Test getting all users with admin token"""
        print("🔍 Testing Get All Users - Admin Access...")
        
        if "admin" not in self.tokens:
            self.log_test("Get All Users Admin", False, "No admin token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens['admin']}"}
        success, response, error = self.make_request("GET", "/users", headers=headers)
        
        if not success:
            self.log_test("Get All Users Admin", False, f"Request failed: {error}")
            return False
            
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                self.log_test("Get All Users Admin", True, f"Retrieved {len(data)} users")
                return True
            else:
                self.log_test("Get All Users Admin", False, f"Expected list of users, got: {data}")
                return False
        else:
            try:
                error_data = response.json()
                self.log_test("Get All Users Admin", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
            except:
                self.log_test("Get All Users Admin", False, f"Status {response.status_code}: {response.text}")
            return False
    
    def test_get_all_users_non_admin(self, role: str) -> bool:
        """Test getting all users with non-admin token"""
        print(f"🔍 Testing Get All Users - {role.title()} Access (Should Fail)...")
        
        if role not in self.tokens:
            self.log_test(f"Get All Users {role.title()}", False, f"No {role} token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        success, response, error = self.make_request("GET", "/users", headers=headers)
        
        if not success:
            self.log_test(f"Get All Users {role.title()}", False, f"Request failed: {error}")
            return False
            
        if response.status_code == 403:
            self.log_test(f"Get All Users {role.title()}", True, "Correctly rejected non-admin access")
            return True
        else:
            self.log_test(f"Get All Users {role.title()}", False, f"Expected 403, got {response.status_code}")
            return False
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("=" * 60)
        print("🚀 LMS Backend API Testing Suite")
        print("=" * 60)
        
        results = []
        
        # Generate unique identifiers for this test run
        import time
        timestamp = str(int(time.time()))
        
        # Test 1: Health Check
        results.append(self.test_health_check())
        
        # Test 2: User Registration (with unique emails)
        results.append(self.test_register_user("admin", f"test_admin_{timestamp}", f"test_admin_{timestamp}@test.com", "Test Admin User", "admin123"))
        results.append(self.test_register_user("mentor", f"test_mentor_{timestamp}", f"test_mentor_{timestamp}@test.com", "Test Mentor User", "mentor123"))
        results.append(self.test_register_user("student", f"test_student_{timestamp}", f"test_student_{timestamp}@test.com", "Test Student User", "student123"))
        
        # Test 3: Duplicate Registration (try to register with existing email)
        results.append(self.test_duplicate_registration())
        
        # Test 4: User Login (use existing users from database)
        results.append(self.test_login("admin", "admin1", "password123"))
        results.append(self.test_login("mentor", "mentor1", "password123"))
        results.append(self.test_login("student", "student1", "password123"))
        
        # Test 5: Invalid Login
        results.append(self.test_invalid_login())
        
        # Test 6: Get Current User (use tokens from login)
        results.append(self.test_get_current_user("admin"))
        results.append(self.test_get_current_user("mentor"))
        results.append(self.test_get_current_user("student"))
        
        # Test 7: Get Current User without token
        results.append(self.test_get_current_user_no_token())
        
        # Test 8: Get All Users (Admin only)
        results.append(self.test_get_all_users_admin())
        results.append(self.test_get_all_users_non_admin("mentor"))
        results.append(self.test_get_all_users_non_admin("student"))
        
        # Summary
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        passed = sum(results)
        total = len(results)
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        if passed == total:
            print("\n🎉 All tests passed! Backend APIs are working correctly.")
            return True
        else:
            print(f"\n⚠️  {total - passed} test(s) failed. Please check the issues above.")
            return False

if __name__ == "__main__":
    tester = LMSAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)