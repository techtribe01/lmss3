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
BACKEND_URL = "https://lms-compliance.preview.emergentagent.com/api"

class LMSAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.tokens = {}  # Store tokens for different users
        self.users = {}   # Store user data
        self.courses = {}  # Store created courses for testing
        
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
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=headers)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers)
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
        
        # Try to register with existing email (we know admin@lms.com exists)
        duplicate_data = {
            "username": "new_unique_user",
            "email": "admin@lms.com",  # This email already exists
            "password": "password123",
            "full_name": "Duplicate User",
            "role": "student"
        }
        
        success, response, error = self.make_request("POST", "/auth/register", duplicate_data)
        
        if not success:
            self.log_test("Duplicate Email", False, f"Request failed: {error}")
            return False
            
        if response.status_code == 400:
            data = response.json()
            if "already exists" in data.get("detail", "").lower():
                self.log_test("Duplicate Email", True, "Correctly rejected duplicate email")
                return True
            else:
                self.log_test("Duplicate Email", False, f"Wrong error message: {data}")
                return False
        else:
            self.log_test("Duplicate Email", False, f"Expected 400, got {response.status_code}")
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

    # ==================== COURSE MANAGEMENT TESTS ====================
    
    def test_create_course(self, role: str, course_data: Dict, should_succeed: bool = True) -> bool:
        """Test course creation with different roles"""
        print(f"🔍 Testing Create Course - {role.title()} User...")
        
        if role not in self.tokens:
            self.log_test(f"Create Course {role.title()}", False, f"No {role} token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        success, response, error = self.make_request("POST", "/courses", course_data, headers)
        
        if not success:
            self.log_test(f"Create Course {role.title()}", False, f"Request failed: {error}")
            return False
            
        if should_succeed:
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data.get("title") == course_data["title"]:
                    # Store course for later tests
                    course_key = f"{role}_course"
                    self.courses[course_key] = data
                    self.log_test(f"Create Course {role.title()}", True, f"Course created successfully. ID: {data['id']}")
                    return True
                else:
                    self.log_test(f"Create Course {role.title()}", False, f"Invalid response data: {data}")
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log_test(f"Create Course {role.title()}", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                except:
                    self.log_test(f"Create Course {role.title()}", False, f"Status {response.status_code}: {response.text}")
                return False
        else:
            # Should fail
            if response.status_code == 403:
                self.log_test(f"Create Course {role.title()}", True, "Correctly rejected unauthorized course creation")
                return True
            else:
                self.log_test(f"Create Course {role.title()}", False, f"Expected 403, got {response.status_code}")
                return False
    
    def test_list_courses(self, role: str) -> bool:
        """Test listing courses with role-based filtering"""
        print(f"🔍 Testing List Courses - {role.title()} User...")
        
        if role not in self.tokens:
            self.log_test(f"List Courses {role.title()}", False, f"No {role} token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        success, response, error = self.make_request("GET", "/courses", headers=headers)
        
        if not success:
            self.log_test(f"List Courses {role.title()}", False, f"Request failed: {error}")
            return False
            
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                self.log_test(f"List Courses {role.title()}", True, f"Retrieved {len(data)} courses")
                return True
            else:
                self.log_test(f"List Courses {role.title()}", False, f"Expected list, got: {type(data)}")
                return False
        else:
            try:
                error_data = response.json()
                self.log_test(f"List Courses {role.title()}", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
            except:
                self.log_test(f"List Courses {role.title()}", False, f"Status {response.status_code}: {response.text}")
            return False
    
    def test_get_single_course(self, role: str, course_id: str, should_succeed: bool = True) -> bool:
        """Test getting a single course by ID"""
        print(f"🔍 Testing Get Single Course - {role.title()} User...")
        
        if role not in self.tokens:
            self.log_test(f"Get Course {role.title()}", False, f"No {role} token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        success, response, error = self.make_request("GET", f"/courses/{course_id}", headers=headers)
        
        if not success:
            self.log_test(f"Get Course {role.title()}", False, f"Request failed: {error}")
            return False
            
        if should_succeed:
            if response.status_code == 200:
                data = response.json()
                if data.get("id") == course_id:
                    self.log_test(f"Get Course {role.title()}", True, f"Retrieved course: {data.get('title')}")
                    return True
                else:
                    self.log_test(f"Get Course {role.title()}", False, f"Course ID mismatch")
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log_test(f"Get Course {role.title()}", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                except:
                    self.log_test(f"Get Course {role.title()}", False, f"Status {response.status_code}: {response.text}")
                return False
        else:
            if response.status_code in [403, 404]:
                self.log_test(f"Get Course {role.title()}", True, "Correctly rejected unauthorized access")
                return True
            else:
                self.log_test(f"Get Course {role.title()}", False, f"Expected 403/404, got {response.status_code}")
                return False
    
    def test_update_course(self, role: str, course_id: str, update_data: Dict, should_succeed: bool = True) -> bool:
        """Test updating a course"""
        print(f"🔍 Testing Update Course - {role.title()} User...")
        
        if role not in self.tokens:
            self.log_test(f"Update Course {role.title()}", False, f"No {role} token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        success, response, error = self.make_request("PUT", f"/courses/{course_id}", update_data, headers)
        
        if not success:
            self.log_test(f"Update Course {role.title()}", False, f"Request failed: {error}")
            return False
            
        if should_succeed:
            if response.status_code == 200:
                data = response.json()
                if data.get("id") == course_id:
                    self.log_test(f"Update Course {role.title()}", True, f"Course updated successfully")
                    return True
                else:
                    self.log_test(f"Update Course {role.title()}", False, f"Course ID mismatch")
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log_test(f"Update Course {role.title()}", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                except:
                    self.log_test(f"Update Course {role.title()}", False, f"Status {response.status_code}: {response.text}")
                return False
        else:
            if response.status_code == 403:
                self.log_test(f"Update Course {role.title()}", True, "Correctly rejected unauthorized update")
                return True
            else:
                self.log_test(f"Update Course {role.title()}", False, f"Expected 403, got {response.status_code}")
                return False
    
    def test_approve_course(self, role: str, course_id: str, approval_status: str, should_succeed: bool = True) -> bool:
        """Test approving/rejecting a course"""
        print(f"🔍 Testing Approve Course - {role.title()} User...")
        
        if role not in self.tokens:
            self.log_test(f"Approve Course {role.title()}", False, f"No {role} token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        approval_data = {"approval_status": approval_status}
        success, response, error = self.make_request("PUT", f"/courses/{course_id}/approve", approval_data, headers)
        
        if not success:
            self.log_test(f"Approve Course {role.title()}", False, f"Request failed: {error}")
            return False
            
        if should_succeed:
            if response.status_code == 200:
                data = response.json()
                if data.get("approval_status") == approval_status:
                    self.log_test(f"Approve Course {role.title()}", True, f"Course status set to: {approval_status}")
                    return True
                else:
                    self.log_test(f"Approve Course {role.title()}", False, f"Status not updated correctly")
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log_test(f"Approve Course {role.title()}", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                except:
                    self.log_test(f"Approve Course {role.title()}", False, f"Status {response.status_code}: {response.text}")
                return False
        else:
            if response.status_code == 403:
                self.log_test(f"Approve Course {role.title()}", True, "Correctly rejected unauthorized approval")
                return True
            else:
                self.log_test(f"Approve Course {role.title()}", False, f"Expected 403, got {response.status_code}")
                return False
    
    def test_delete_course(self, role: str, course_id: str, should_succeed: bool = True) -> bool:
        """Test deleting a course"""
        print(f"🔍 Testing Delete Course - {role.title()} User...")
        
        if role not in self.tokens:
            self.log_test(f"Delete Course {role.title()}", False, f"No {role} token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        success, response, error = self.make_request("DELETE", f"/courses/{course_id}", headers=headers)
        
        if not success:
            self.log_test(f"Delete Course {role.title()}", False, f"Request failed: {error}")
            return False
            
        if should_succeed:
            if response.status_code == 200:
                self.log_test(f"Delete Course {role.title()}", True, "Course deleted successfully")
                return True
            else:
                try:
                    error_data = response.json()
                    self.log_test(f"Delete Course {role.title()}", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                except:
                    self.log_test(f"Delete Course {role.title()}", False, f"Status {response.status_code}: {response.text}")
                return False
        else:
            if response.status_code == 403:
                self.log_test(f"Delete Course {role.title()}", True, "Correctly rejected unauthorized deletion")
                return True
            else:
                self.log_test(f"Delete Course {role.title()}", False, f"Expected 403, got {response.status_code}")
                return False
    
    def test_get_mentor_courses(self, role: str, mentor_id: str, should_succeed: bool = True) -> bool:
        """Test getting courses for a specific mentor"""
        print(f"🔍 Testing Get Mentor Courses - {role.title()} User...")
        
        if role not in self.tokens:
            self.log_test(f"Get Mentor Courses {role.title()}", False, f"No {role} token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        success, response, error = self.make_request("GET", f"/courses/mentor/{mentor_id}", headers=headers)
        
        if not success:
            self.log_test(f"Get Mentor Courses {role.title()}", False, f"Request failed: {error}")
            return False
            
        if should_succeed:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test(f"Get Mentor Courses {role.title()}", True, f"Retrieved {len(data)} mentor courses")
                    return True
                else:
                    self.log_test(f"Get Mentor Courses {role.title()}", False, f"Expected list, got: {type(data)}")
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log_test(f"Get Mentor Courses {role.title()}", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                except:
                    self.log_test(f"Get Mentor Courses {role.title()}", False, f"Status {response.status_code}: {response.text}")
                return False
        else:
            if response.status_code == 403:
                self.log_test(f"Get Mentor Courses {role.title()}", True, "Correctly rejected unauthorized access")
                return True
            else:
                self.log_test(f"Get Mentor Courses {role.title()}", False, f"Expected 403, got {response.status_code}")
                return False

    def run_course_management_tests(self):
        """Run comprehensive course management tests"""
        print("\n" + "=" * 60)
        print("🎓 COURSE MANAGEMENT TESTING")
        print("=" * 60)
        
        results = []
        
        # Test data for course creation
        admin_course_data = {
            "title": "Advanced Python Programming",
            "description": "Comprehensive Python course for advanced learners",
            "mentor_id": self.users.get("mentor", {}).get("id"),
            "zoom_id": "123-456-789"
        }
        
        mentor_course_data = {
            "title": "JavaScript Fundamentals",
            "description": "Learn JavaScript from basics to advanced",
            "teams_id": "js-team-001"
        }
        
        # Test 1: Course Creation
        print("\n📝 Testing Course Creation...")
        results.append(self.test_create_course("admin", admin_course_data, True))
        results.append(self.test_create_course("mentor", mentor_course_data, True))
        results.append(self.test_create_course("student", mentor_course_data, False))  # Should fail
        
        # Test 2: List Courses (role-based filtering)
        print("\n📋 Testing Course Listing...")
        results.append(self.test_list_courses("admin"))
        results.append(self.test_list_courses("mentor"))
        results.append(self.test_list_courses("student"))
        
        # Test 3: Get Single Course (access control)
        print("\n🔍 Testing Single Course Access...")
        if "admin_course" in self.courses:
            course_id = self.courses["admin_course"]["id"]
            results.append(self.test_get_single_course("admin", course_id, True))
            results.append(self.test_get_single_course("mentor", course_id, True))  # Should see if approved
            results.append(self.test_get_single_course("student", course_id, False))  # Should fail if pending
        
        # Test 4: Course Updates
        print("\n✏️ Testing Course Updates...")
        if "mentor_course" in self.courses:
            mentor_course_id = self.courses["mentor_course"]["id"]
            update_data = {"title": "Updated JavaScript Course", "description": "Updated description"}
            results.append(self.test_update_course("mentor", mentor_course_id, update_data, True))  # Own course
            results.append(self.test_update_course("student", mentor_course_id, update_data, False))  # Should fail
            
        if "admin_course" in self.courses:
            admin_course_id = self.courses["admin_course"]["id"]
            results.append(self.test_update_course("admin", admin_course_id, update_data, True))  # Admin can edit any
        
        # Test 5: Course Approval Workflow
        print("\n✅ Testing Course Approval...")
        if "mentor_course" in self.courses:
            mentor_course_id = self.courses["mentor_course"]["id"]
            results.append(self.test_approve_course("admin", mentor_course_id, "approved", True))
            results.append(self.test_approve_course("mentor", mentor_course_id, "pending", False))  # Should fail
            results.append(self.test_approve_course("student", mentor_course_id, "rejected", False))  # Should fail
        
        # Test 6: Get Mentor Courses
        print("\n👨‍🏫 Testing Mentor Course Access...")
        if "mentor" in self.users:
            mentor_id = self.users["mentor"]["id"]
            results.append(self.test_get_mentor_courses("admin", mentor_id, True))  # Admin can view any
            results.append(self.test_get_mentor_courses("mentor", mentor_id, True))  # Own courses
            results.append(self.test_get_mentor_courses("student", mentor_id, False))  # Should fail
        
        # Test 7: Course Deletion (Admin only)
        print("\n🗑️ Testing Course Deletion...")
        if "admin_course" in self.courses:
            admin_course_id = self.courses["admin_course"]["id"]
            results.append(self.test_delete_course("mentor", admin_course_id, False))  # Should fail
            results.append(self.test_delete_course("student", admin_course_id, False))  # Should fail
            results.append(self.test_delete_course("admin", admin_course_id, True))  # Should succeed
        
        return results
    
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
        
        # Test 4: User Login (use newly registered users)
        results.append(self.test_login("admin", f"test_admin_{timestamp}", "admin123"))
        results.append(self.test_login("mentor", f"test_mentor_{timestamp}", "mentor123"))
        results.append(self.test_login("student", f"test_student_{timestamp}", "student123"))
        
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
        
        # Test 9: Course Management Tests
        course_results = self.run_course_management_tests()
        results.extend(course_results)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        passed = sum(results)
        total = len(results)
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        if passed == total:
            print("\n🎉 All tests passed! Backend APIs are working correctly.")
            print("✅ Authentication system: WORKING")
            print("✅ Course management system: WORKING")
            return True
        else:
            print(f"\n⚠️  {total - passed} test(s) failed. Please check the issues above.")
            return False

if __name__ == "__main__":
    tester = LMSAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)