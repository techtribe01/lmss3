#!/usr/bin/env python3
"""
LMS Backend API Testing Suite
Tests all authentication and user management endpoints
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

# Get backend URL from supervisor configuration
BACKEND_URL = "https://auth-creds-update.preview.emergentagent.com/api"

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
    
    # ==================== ENROLLMENT MANAGEMENT TESTS ====================
    
    def test_enroll_student(self, role: str, course_id: str, should_succeed: bool = True) -> bool:
        """Test student enrollment in a course"""
        print(f"🔍 Testing Student Enrollment - {role.title()} User...")
        
        if role not in self.tokens:
            self.log_test(f"Enroll Student {role.title()}", False, f"No {role} token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        enrollment_data = {"course_id": course_id}
        success, response, error = self.make_request("POST", "/enrollments", enrollment_data, headers)
        
        if not success:
            self.log_test(f"Enroll Student {role.title()}", False, f"Request failed: {error}")
            return False
            
        if should_succeed:
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data.get("course_id") == course_id:
                    self.log_test(f"Enroll Student {role.title()}", True, f"Student enrolled successfully. Enrollment ID: {data['id']}")
                    return True
                else:
                    self.log_test(f"Enroll Student {role.title()}", False, f"Invalid response data: {data}")
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log_test(f"Enroll Student {role.title()}", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                except:
                    self.log_test(f"Enroll Student {role.title()}", False, f"Status {response.status_code}: {response.text}")
                return False
        else:
            if response.status_code in [403, 400]:
                self.log_test(f"Enroll Student {role.title()}", True, "Correctly rejected unauthorized enrollment")
                return True
            else:
                self.log_test(f"Enroll Student {role.title()}", False, f"Expected 403/400, got {response.status_code}")
                return False
    
    def test_get_user_enrollments(self, role: str, should_succeed: bool = True) -> bool:
        """Test getting current user's enrollments"""
        print(f"🔍 Testing Get User Enrollments - {role.title()} User...")
        
        if role not in self.tokens:
            self.log_test(f"Get User Enrollments {role.title()}", False, f"No {role} token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        success, response, error = self.make_request("GET", "/enrollments", headers=headers)
        
        if not success:
            self.log_test(f"Get User Enrollments {role.title()}", False, f"Request failed: {error}")
            return False
            
        if should_succeed:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test(f"Get User Enrollments {role.title()}", True, f"Retrieved {len(data)} enrollments")
                    return True
                else:
                    self.log_test(f"Get User Enrollments {role.title()}", False, f"Expected list, got: {type(data)}")
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log_test(f"Get User Enrollments {role.title()}", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                except:
                    self.log_test(f"Get User Enrollments {role.title()}", False, f"Status {response.status_code}: {response.text}")
                return False
        else:
            if response.status_code == 403:
                self.log_test(f"Get User Enrollments {role.title()}", True, "Correctly rejected unauthorized access")
                return True
            else:
                self.log_test(f"Get User Enrollments {role.title()}", False, f"Expected 403, got {response.status_code}")
                return False
    
    def test_get_student_enrollments(self, role: str, student_id: str, should_succeed: bool = True) -> bool:
        """Test getting enrollments for a specific student"""
        print(f"🔍 Testing Get Student Enrollments - {role.title()} User...")
        
        if role not in self.tokens:
            self.log_test(f"Get Student Enrollments {role.title()}", False, f"No {role} token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        success, response, error = self.make_request("GET", f"/enrollments/student/{student_id}", headers=headers)
        
        if not success:
            self.log_test(f"Get Student Enrollments {role.title()}", False, f"Request failed: {error}")
            return False
            
        if should_succeed:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test(f"Get Student Enrollments {role.title()}", True, f"Retrieved {len(data)} student enrollments")
                    return True
                else:
                    self.log_test(f"Get Student Enrollments {role.title()}", False, f"Expected list, got: {type(data)}")
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log_test(f"Get Student Enrollments {role.title()}", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                except:
                    self.log_test(f"Get Student Enrollments {role.title()}", False, f"Status {response.status_code}: {response.text}")
                return False
        else:
            if response.status_code == 403:
                self.log_test(f"Get Student Enrollments {role.title()}", True, "Correctly rejected unauthorized access")
                return True
            else:
                self.log_test(f"Get Student Enrollments {role.title()}", False, f"Expected 403, got {response.status_code}")
                return False
    
    def test_get_course_enrollments(self, role: str, course_id: str, should_succeed: bool = True) -> bool:
        """Test getting enrollments for a specific course"""
        print(f"🔍 Testing Get Course Enrollments - {role.title()} User...")
        
        if role not in self.tokens:
            self.log_test(f"Get Course Enrollments {role.title()}", False, f"No {role} token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        success, response, error = self.make_request("GET", f"/enrollments/course/{course_id}", headers=headers)
        
        if not success:
            self.log_test(f"Get Course Enrollments {role.title()}", False, f"Request failed: {error}")
            return False
            
        if should_succeed:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test(f"Get Course Enrollments {role.title()}", True, f"Retrieved {len(data)} course enrollments")
                    return True
                else:
                    self.log_test(f"Get Course Enrollments {role.title()}", False, f"Expected list, got: {type(data)}")
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log_test(f"Get Course Enrollments {role.title()}", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                except:
                    self.log_test(f"Get Course Enrollments {role.title()}", False, f"Status {response.status_code}: {response.text}")
                return False
        else:
            if response.status_code == 403:
                self.log_test(f"Get Course Enrollments {role.title()}", True, "Correctly rejected unauthorized access")
                return True
            else:
                self.log_test(f"Get Course Enrollments {role.title()}", False, f"Expected 403, got {response.status_code}")
                return False
    
    def test_unenroll_student(self, role: str, course_id: str, student_id: str, should_succeed: bool = True) -> bool:
        """Test unenrolling a student from a course"""
        print(f"🔍 Testing Unenroll Student - {role.title()} User...")
        
        if role not in self.tokens:
            self.log_test(f"Unenroll Student {role.title()}", False, f"No {role} token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        success, response, error = self.make_request("DELETE", f"/enrollments/{course_id}/student/{student_id}", headers=headers)
        
        if not success:
            self.log_test(f"Unenroll Student {role.title()}", False, f"Request failed: {error}")
            return False
            
        if should_succeed:
            if response.status_code == 200:
                self.log_test(f"Unenroll Student {role.title()}", True, "Student unenrolled successfully")
                return True
            else:
                try:
                    error_data = response.json()
                    self.log_test(f"Unenroll Student {role.title()}", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                except:
                    self.log_test(f"Unenroll Student {role.title()}", False, f"Status {response.status_code}: {response.text}")
                return False
        else:
            if response.status_code == 403:
                self.log_test(f"Unenroll Student {role.title()}", True, "Correctly rejected unauthorized unenrollment")
                return True
            else:
                self.log_test(f"Unenroll Student {role.title()}", False, f"Expected 403, got {response.status_code}")
                return False
    
    def test_update_enrollment_status(self, role: str, course_id: str, student_id: str, status: str, should_succeed: bool = True) -> bool:
        """Test updating enrollment status"""
        print(f"🔍 Testing Update Enrollment Status - {role.title()} User...")
        
        if role not in self.tokens:
            self.log_test(f"Update Enrollment Status {role.title()}", False, f"No {role} token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        status_data = {"completion_status": status}
        success, response, error = self.make_request("PUT", f"/enrollments/{course_id}/student/{student_id}/status", status_data, headers)
        
        if not success:
            self.log_test(f"Update Enrollment Status {role.title()}", False, f"Request failed: {error}")
            return False
            
        if should_succeed:
            if response.status_code == 200:
                data = response.json()
                if data.get("completion_status") == status:
                    self.log_test(f"Update Enrollment Status {role.title()}", True, f"Status updated to: {status}")
                    return True
                else:
                    self.log_test(f"Update Enrollment Status {role.title()}", False, f"Status not updated correctly")
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log_test(f"Update Enrollment Status {role.title()}", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                except:
                    self.log_test(f"Update Enrollment Status {role.title()}", False, f"Status {response.status_code}: {response.text}")
                return False
        else:
            if response.status_code == 403:
                self.log_test(f"Update Enrollment Status {role.title()}", True, "Correctly rejected unauthorized status update")
                return True
            else:
                self.log_test(f"Update Enrollment Status {role.title()}", False, f"Expected 403, got {response.status_code}")
                return False

    # ==================== TASK/ASSIGNMENT MANAGEMENT TESTS ====================
    
    def test_create_task(self, role: str, task_data: Dict, should_succeed: bool = True) -> bool:
        """Test creating a task/assignment"""
        print(f"🔍 Testing Create Task - {role.title()} User...")
        
        if role not in self.tokens:
            self.log_test(f"Create Task {role.title()}", False, f"No {role} token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        success, response, error = self.make_request("POST", "/tasks", task_data, headers)
        
        if not success:
            self.log_test(f"Create Task {role.title()}", False, f"Request failed: {error}")
            return False
            
        if should_succeed:
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data.get("title") == task_data["title"]:
                    # Store task for later tests
                    task_key = f"{role}_task"
                    if not hasattr(self, 'tasks'):
                        self.tasks = {}
                    self.tasks[task_key] = data
                    self.log_test(f"Create Task {role.title()}", True, f"Task created successfully. ID: {data['id']}")
                    return True
                else:
                    self.log_test(f"Create Task {role.title()}", False, f"Invalid response data: {data}")
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log_test(f"Create Task {role.title()}", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                except:
                    self.log_test(f"Create Task {role.title()}", False, f"Status {response.status_code}: {response.text}")
                return False
        else:
            if response.status_code == 403:
                self.log_test(f"Create Task {role.title()}", True, "Correctly rejected unauthorized task creation")
                return True
            else:
                self.log_test(f"Create Task {role.title()}", False, f"Expected 403, got {response.status_code}")
                return False
    
    def test_get_tasks(self, role: str, course_id: str = None, should_succeed: bool = True) -> bool:
        """Test getting tasks (optionally filtered by course)"""
        print(f"🔍 Testing Get Tasks - {role.title()} User...")
        
        if role not in self.tokens:
            self.log_test(f"Get Tasks {role.title()}", False, f"No {role} token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        endpoint = "/tasks"
        if course_id:
            endpoint += f"?course_id={course_id}"
        success, response, error = self.make_request("GET", endpoint, headers=headers)
        
        if not success:
            self.log_test(f"Get Tasks {role.title()}", False, f"Request failed: {error}")
            return False
            
        if should_succeed:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test(f"Get Tasks {role.title()}", True, f"Retrieved {len(data)} tasks")
                    return True
                else:
                    self.log_test(f"Get Tasks {role.title()}", False, f"Expected list, got: {type(data)}")
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log_test(f"Get Tasks {role.title()}", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                except:
                    self.log_test(f"Get Tasks {role.title()}", False, f"Status {response.status_code}: {response.text}")
                return False
        else:
            if response.status_code == 403:
                self.log_test(f"Get Tasks {role.title()}", True, "Correctly rejected unauthorized access")
                return True
            else:
                self.log_test(f"Get Tasks {role.title()}", False, f"Expected 403, got {response.status_code}")
                return False
    
    def test_get_single_task(self, role: str, task_id: str, should_succeed: bool = True) -> bool:
        """Test getting a specific task"""
        print(f"🔍 Testing Get Single Task - {role.title()} User...")
        
        if role not in self.tokens:
            self.log_test(f"Get Single Task {role.title()}", False, f"No {role} token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        success, response, error = self.make_request("GET", f"/tasks/{task_id}", headers=headers)
        
        if not success:
            self.log_test(f"Get Single Task {role.title()}", False, f"Request failed: {error}")
            return False
            
        if should_succeed:
            if response.status_code == 200:
                data = response.json()
                if data.get("id") == task_id:
                    self.log_test(f"Get Single Task {role.title()}", True, f"Retrieved task: {data.get('title')}")
                    return True
                else:
                    self.log_test(f"Get Single Task {role.title()}", False, f"Task ID mismatch")
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log_test(f"Get Single Task {role.title()}", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                except:
                    self.log_test(f"Get Single Task {role.title()}", False, f"Status {response.status_code}: {response.text}")
                return False
        else:
            if response.status_code in [403, 404]:
                self.log_test(f"Get Single Task {role.title()}", True, "Correctly rejected unauthorized access")
                return True
            else:
                self.log_test(f"Get Single Task {role.title()}", False, f"Expected 403/404, got {response.status_code}")
                return False
    
    def test_update_task(self, role: str, task_id: str, update_data: Dict, should_succeed: bool = True) -> bool:
        """Test updating a task"""
        print(f"🔍 Testing Update Task - {role.title()} User...")
        
        if role not in self.tokens:
            self.log_test(f"Update Task {role.title()}", False, f"No {role} token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        success, response, error = self.make_request("PUT", f"/tasks/{task_id}", update_data, headers)
        
        if not success:
            self.log_test(f"Update Task {role.title()}", False, f"Request failed: {error}")
            return False
            
        if should_succeed:
            if response.status_code == 200:
                data = response.json()
                if data.get("id") == task_id:
                    self.log_test(f"Update Task {role.title()}", True, f"Task updated successfully")
                    return True
                else:
                    self.log_test(f"Update Task {role.title()}", False, f"Task ID mismatch")
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log_test(f"Update Task {role.title()}", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                except:
                    self.log_test(f"Update Task {role.title()}", False, f"Status {response.status_code}: {response.text}")
                return False
        else:
            if response.status_code == 403:
                self.log_test(f"Update Task {role.title()}", True, "Correctly rejected unauthorized update")
                return True
            else:
                self.log_test(f"Update Task {role.title()}", False, f"Expected 403, got {response.status_code}")
                return False
    
    def test_delete_task(self, role: str, task_id: str, should_succeed: bool = True) -> bool:
        """Test deleting a task"""
        print(f"🔍 Testing Delete Task - {role.title()} User...")
        
        if role not in self.tokens:
            self.log_test(f"Delete Task {role.title()}", False, f"No {role} token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        success, response, error = self.make_request("DELETE", f"/tasks/{task_id}", headers=headers)
        
        if not success:
            self.log_test(f"Delete Task {role.title()}", False, f"Request failed: {error}")
            return False
            
        if should_succeed:
            if response.status_code == 200:
                self.log_test(f"Delete Task {role.title()}", True, "Task deleted successfully")
                return True
            else:
                try:
                    error_data = response.json()
                    self.log_test(f"Delete Task {role.title()}", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                except:
                    self.log_test(f"Delete Task {role.title()}", False, f"Status {response.status_code}: {response.text}")
                return False
        else:
            if response.status_code == 403:
                self.log_test(f"Delete Task {role.title()}", True, "Correctly rejected unauthorized deletion")
                return True
            else:
                self.log_test(f"Delete Task {role.title()}", False, f"Expected 403, got {response.status_code}")
                return False
    
    def test_submit_task(self, role: str, submission_data: Dict, should_succeed: bool = True) -> bool:
        """Test submitting a task"""
        print(f"🔍 Testing Submit Task - {role.title()} User...")
        
        if role not in self.tokens:
            self.log_test(f"Submit Task {role.title()}", False, f"No {role} token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        success, response, error = self.make_request("POST", "/task-submissions", submission_data, headers)
        
        if not success:
            self.log_test(f"Submit Task {role.title()}", False, f"Request failed: {error}")
            return False
            
        if should_succeed:
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data.get("task_id") == submission_data["task_id"]:
                    # Store submission for later tests
                    if not hasattr(self, 'submissions'):
                        self.submissions = {}
                    self.submissions[f"{role}_submission"] = data
                    self.log_test(f"Submit Task {role.title()}", True, f"Task submitted successfully. Submission ID: {data['id']}")
                    return True
                else:
                    self.log_test(f"Submit Task {role.title()}", False, f"Invalid response data: {data}")
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log_test(f"Submit Task {role.title()}", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                except:
                    self.log_test(f"Submit Task {role.title()}", False, f"Status {response.status_code}: {response.text}")
                return False
        else:
            if response.status_code in [403, 400]:
                self.log_test(f"Submit Task {role.title()}", True, "Correctly rejected unauthorized submission")
                return True
            else:
                self.log_test(f"Submit Task {role.title()}", False, f"Expected 403/400, got {response.status_code}")
                return False
    
    def test_get_task_submissions(self, role: str, task_id: str = None, should_succeed: bool = True) -> bool:
        """Test getting task submissions"""
        print(f"🔍 Testing Get Task Submissions - {role.title()} User...")
        
        if role not in self.tokens:
            self.log_test(f"Get Task Submissions {role.title()}", False, f"No {role} token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        endpoint = "/task-submissions"
        if task_id:
            endpoint += f"?task_id={task_id}"
        success, response, error = self.make_request("GET", endpoint, headers=headers)
        
        if not success:
            self.log_test(f"Get Task Submissions {role.title()}", False, f"Request failed: {error}")
            return False
            
        if should_succeed:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test(f"Get Task Submissions {role.title()}", True, f"Retrieved {len(data)} submissions")
                    return True
                else:
                    self.log_test(f"Get Task Submissions {role.title()}", False, f"Expected list, got: {type(data)}")
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log_test(f"Get Task Submissions {role.title()}", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                except:
                    self.log_test(f"Get Task Submissions {role.title()}", False, f"Status {response.status_code}: {response.text}")
                return False
        else:
            if response.status_code == 403:
                self.log_test(f"Get Task Submissions {role.title()}", True, "Correctly rejected unauthorized access")
                return True
            else:
                self.log_test(f"Get Task Submissions {role.title()}", False, f"Expected 403, got {response.status_code}")
                return False
    
    def test_grade_submission(self, role: str, submission_id: str, grade_data: Dict, should_succeed: bool = True) -> bool:
        """Test grading a task submission"""
        print(f"🔍 Testing Grade Submission - {role.title()} User...")
        
        if role not in self.tokens:
            self.log_test(f"Grade Submission {role.title()}", False, f"No {role} token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        success, response, error = self.make_request("PUT", f"/task-submissions/{submission_id}/grade", grade_data, headers)
        
        if not success:
            self.log_test(f"Grade Submission {role.title()}", False, f"Request failed: {error}")
            return False
            
        if should_succeed:
            if response.status_code == 200:
                data = response.json()
                if data.get("grade") == grade_data["grade"]:
                    self.log_test(f"Grade Submission {role.title()}", True, f"Submission graded successfully. Grade: {data['grade']}")
                    return True
                else:
                    self.log_test(f"Grade Submission {role.title()}", False, f"Grade not updated correctly")
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log_test(f"Grade Submission {role.title()}", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                except:
                    self.log_test(f"Grade Submission {role.title()}", False, f"Status {response.status_code}: {response.text}")
                return False
        else:
            if response.status_code == 403:
                self.log_test(f"Grade Submission {role.title()}", True, "Correctly rejected unauthorized grading")
                return True
            else:
                self.log_test(f"Grade Submission {role.title()}", False, f"Expected 403, got {response.status_code}")
                return False

    def run_enrollment_tests(self):
        """Run comprehensive enrollment management tests"""
        print("\n" + "=" * 60)
        print("📚 ENROLLMENT MANAGEMENT TESTING")
        print("=" * 60)
        
        results = []
        
        # Ensure we have an approved course for enrollment testing
        if "mentor_course" in self.courses:
            course_id = self.courses["mentor_course"]["id"]
            # Approve the course first
            if "admin" in self.tokens:
                headers = {"Authorization": f"Bearer {self.tokens['admin']}"}
                approval_data = {"approval_status": "approved"}
                self.make_request("PUT", f"/courses/{course_id}/approve", approval_data, headers)
        
        # Test 1: Student Enrollment
        print("\n📝 Testing Student Enrollment...")
        if "mentor_course" in self.courses:
            course_id = self.courses["mentor_course"]["id"]
            results.append(self.test_enroll_student("student", course_id, True))
            results.append(self.test_enroll_student("mentor", course_id, False))  # Should fail
            results.append(self.test_enroll_student("admin", course_id, True))  # Admin can enroll
        
        # Test 2: Get User Enrollments
        print("\n📋 Testing Get User Enrollments...")
        results.append(self.test_get_user_enrollments("student", True))
        results.append(self.test_get_user_enrollments("mentor", False))  # Should fail
        results.append(self.test_get_user_enrollments("admin", False))  # Should fail
        
        # Test 3: Get Student Enrollments (Admin/Mentor access)
        print("\n👨‍🎓 Testing Get Student Enrollments...")
        if "student" in self.users:
            student_id = self.users["student"]["id"]
            results.append(self.test_get_student_enrollments("admin", student_id, True))
            results.append(self.test_get_student_enrollments("mentor", student_id, True))
            results.append(self.test_get_student_enrollments("student", student_id, False))  # Should fail
        
        # Test 4: Get Course Enrollments
        print("\n🎓 Testing Get Course Enrollments...")
        if "mentor_course" in self.courses:
            course_id = self.courses["mentor_course"]["id"]
            results.append(self.test_get_course_enrollments("admin", course_id, True))
            results.append(self.test_get_course_enrollments("mentor", course_id, True))
            results.append(self.test_get_course_enrollments("student", course_id, False))  # Should fail
        
        # Test 5: Update Enrollment Status
        print("\n✏️ Testing Update Enrollment Status...")
        if "mentor_course" in self.courses and "student" in self.users:
            course_id = self.courses["mentor_course"]["id"]
            student_id = self.users["student"]["id"]
            results.append(self.test_update_enrollment_status("admin", course_id, student_id, "completed", True))
            results.append(self.test_update_enrollment_status("mentor", course_id, student_id, "in_progress", True))
            results.append(self.test_update_enrollment_status("student", course_id, student_id, "completed", False))  # Should fail
        
        # Test 6: Unenroll Student
        print("\n🚪 Testing Student Unenrollment...")
        if "mentor_course" in self.courses and "student" in self.users:
            course_id = self.courses["mentor_course"]["id"]
            student_id = self.users["student"]["id"]
            results.append(self.test_unenroll_student("student", course_id, student_id, True))  # Student can unenroll self
            # Re-enroll for admin test
            self.test_enroll_student("student", course_id, True)
            results.append(self.test_unenroll_student("admin", course_id, student_id, True))  # Admin can unenroll
        
        return results

    def run_task_management_tests(self):
        """Run comprehensive task/assignment management tests"""
        print("\n" + "=" * 60)
        print("📋 TASK/ASSIGNMENT MANAGEMENT TESTING")
        print("=" * 60)
        
        results = []
        
        # Test 1: Task Creation
        print("\n📝 Testing Task Creation...")
        if "mentor_course" in self.courses:
            course_id = self.courses["mentor_course"]["id"]
            task_data = {
                "course_id": course_id,
                "title": "Python Programming Assignment",
                "description": "Complete the Python exercises and submit your code",
                "due_date": "2025-02-15T23:59:59Z"
            }
            results.append(self.test_create_task("mentor", task_data, True))
            results.append(self.test_create_task("admin", task_data, True))
            results.append(self.test_create_task("student", task_data, False))  # Should fail
        
        # Test 2: Get Tasks
        print("\n📋 Testing Get Tasks...")
        results.append(self.test_get_tasks("admin", None, True))
        results.append(self.test_get_tasks("mentor", None, True))
        results.append(self.test_get_tasks("student", None, True))
        
        # Test with course filter
        if "mentor_course" in self.courses:
            course_id = self.courses["mentor_course"]["id"]
            results.append(self.test_get_tasks("mentor", course_id, True))
            results.append(self.test_get_tasks("student", course_id, True))  # If enrolled
        
        # Test 3: Get Single Task
        print("\n🔍 Testing Get Single Task...")
        if hasattr(self, 'tasks') and "mentor_task" in self.tasks:
            task_id = self.tasks["mentor_task"]["id"]
            results.append(self.test_get_single_task("admin", task_id, True))
            results.append(self.test_get_single_task("mentor", task_id, True))
            results.append(self.test_get_single_task("student", task_id, True))  # If enrolled in course
        
        # Test 4: Update Task
        print("\n✏️ Testing Update Task...")
        if hasattr(self, 'tasks') and "mentor_task" in self.tasks:
            task_id = self.tasks["mentor_task"]["id"]
            update_data = {
                "title": "Updated Python Assignment",
                "description": "Updated description with more details"
            }
            results.append(self.test_update_task("mentor", task_id, update_data, True))
            results.append(self.test_update_task("admin", task_id, update_data, True))
            results.append(self.test_update_task("student", task_id, update_data, False))  # Should fail
        
        # Test 5: Task Submission
        print("\n📤 Testing Task Submission...")
        if hasattr(self, 'tasks') and "mentor_task" in self.tasks:
            task_id = self.tasks["mentor_task"]["id"]
            submission_data = {
                "task_id": task_id,
                "content": "Here is my solution to the Python assignment. I have completed all the exercises and tested the code thoroughly.",
                "file_url": "https://example.com/student_submission.py"
            }
            results.append(self.test_submit_task("student", submission_data, True))
            results.append(self.test_submit_task("mentor", submission_data, False))  # Should fail
            results.append(self.test_submit_task("admin", submission_data, False))  # Should fail
        
        # Test 6: Get Task Submissions
        print("\n📥 Testing Get Task Submissions...")
        results.append(self.test_get_task_submissions("student", None, True))  # Own submissions
        results.append(self.test_get_task_submissions("mentor", None, True))  # Course submissions
        results.append(self.test_get_task_submissions("admin", None, True))  # All submissions
        
        # Test with task filter
        if hasattr(self, 'tasks') and "mentor_task" in self.tasks:
            task_id = self.tasks["mentor_task"]["id"]
            results.append(self.test_get_task_submissions("mentor", task_id, True))
            results.append(self.test_get_task_submissions("admin", task_id, True))
        
        # Test 7: Grade Submission
        print("\n📊 Testing Grade Submission...")
        if hasattr(self, 'submissions') and "student_submission" in self.submissions:
            submission_id = self.submissions["student_submission"]["id"]
            grade_data = {
                "grade": 85.5,
                "feedback": "Good work! Your solution is correct and well-structured. Consider adding more comments for better readability."
            }
            results.append(self.test_grade_submission("mentor", submission_id, grade_data, True))
            results.append(self.test_grade_submission("admin", submission_id, grade_data, True))
            results.append(self.test_grade_submission("student", submission_id, grade_data, False))  # Should fail
        
        # Test 8: Delete Task
        print("\n🗑️ Testing Delete Task...")
        if hasattr(self, 'tasks') and "mentor_task" in self.tasks:
            task_id = self.tasks["mentor_task"]["id"]
            results.append(self.test_delete_task("student", task_id, False))  # Should fail
            results.append(self.test_delete_task("mentor", task_id, True))  # Should succeed
        
        return results

    # ==================== ATTENDANCE TRACKING TESTS ====================
    
    def test_checkin_attendance(self, role: str, course_id: str, date: str, should_succeed: bool = True) -> bool:
        """Test student check-in to course"""
        print(f"🔍 Testing Check-in Attendance - {role.title()} User...")
        
        if role not in self.tokens:
            self.log_test(f"Check-in Attendance {role.title()}", False, f"No {role} token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        attendance_data = {"course_id": course_id, "date": date}
        success, response, error = self.make_request("POST", "/attendance/checkin", attendance_data, headers)
        
        if not success:
            self.log_test(f"Check-in Attendance {role.title()}", False, f"Request failed: {error}")
            return False
            
        if should_succeed:
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data.get("course_id") == course_id:
                    self.log_test(f"Check-in Attendance {role.title()}", True, f"Check-in successful. ID: {data['id']}")
                    return True
                else:
                    self.log_test(f"Check-in Attendance {role.title()}", False, f"Invalid response data: {data}")
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log_test(f"Check-in Attendance {role.title()}", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                except:
                    self.log_test(f"Check-in Attendance {role.title()}", False, f"Status {response.status_code}: {response.text}")
                return False
        else:
            if response.status_code == 403:
                self.log_test(f"Check-in Attendance {role.title()}", True, "Correctly rejected unauthorized check-in")
                return True
            else:
                self.log_test(f"Check-in Attendance {role.title()}", False, f"Expected 403, got {response.status_code}")
                return False
    
    def test_checkout_attendance(self, role: str, course_id: str, date: str, should_succeed: bool = True) -> bool:
        """Test student check-out from course"""
        print(f"🔍 Testing Check-out Attendance - {role.title()} User...")
        
        if role not in self.tokens:
            self.log_test(f"Check-out Attendance {role.title()}", False, f"No {role} token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        success, response, error = self.make_request("POST", f"/attendance/checkout?course_id={course_id}&date={date}", headers=headers)
        
        if not success:
            self.log_test(f"Check-out Attendance {role.title()}", False, f"Request failed: {error}")
            return False
            
        if should_succeed:
            if response.status_code == 200:
                self.log_test(f"Check-out Attendance {role.title()}", True, "Check-out successful")
                return True
            else:
                try:
                    error_data = response.json()
                    self.log_test(f"Check-out Attendance {role.title()}", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                except:
                    self.log_test(f"Check-out Attendance {role.title()}", False, f"Status {response.status_code}: {response.text}")
                return False
        else:
            if response.status_code == 403:
                self.log_test(f"Check-out Attendance {role.title()}", True, "Correctly rejected unauthorized check-out")
                return True
            else:
                self.log_test(f"Check-out Attendance {role.title()}", False, f"Expected 403, got {response.status_code}")
                return False
    
    def test_get_attendance_records(self, role: str, course_id: str = None, should_succeed: bool = True) -> bool:
        """Test getting attendance records"""
        print(f"🔍 Testing Get Attendance Records - {role.title()} User...")
        
        if role not in self.tokens:
            self.log_test(f"Get Attendance Records {role.title()}", False, f"No {role} token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        endpoint = "/attendance"
        if course_id:
            endpoint += f"?course_id={course_id}"
        success, response, error = self.make_request("GET", endpoint, headers=headers)
        
        if not success:
            self.log_test(f"Get Attendance Records {role.title()}", False, f"Request failed: {error}")
            return False
            
        if should_succeed:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test(f"Get Attendance Records {role.title()}", True, f"Retrieved {len(data)} attendance records")
                    return True
                else:
                    self.log_test(f"Get Attendance Records {role.title()}", False, f"Expected list, got: {type(data)}")
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log_test(f"Get Attendance Records {role.title()}", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                except:
                    self.log_test(f"Get Attendance Records {role.title()}", False, f"Status {response.status_code}: {response.text}")
                return False
        else:
            if response.status_code == 403:
                self.log_test(f"Get Attendance Records {role.title()}", True, "Correctly rejected unauthorized access")
                return True
            else:
                self.log_test(f"Get Attendance Records {role.title()}", False, f"Expected 403, got {response.status_code}")
                return False

    def run_attendance_tests(self):
        """Run comprehensive attendance tracking tests"""
        print("\n" + "=" * 60)
        print("📅 ATTENDANCE TRACKING TESTING")
        print("=" * 60)
        
        results = []
        
        # Ensure we have an approved course and enrolled student
        if "mentor_course" in self.courses:
            course_id = self.courses["mentor_course"]["id"]
            today = "2025-01-01"
            
            # Test 1: Student Check-in
            print("\n📝 Testing Student Check-in...")
            results.append(self.test_checkin_attendance("student", course_id, today, True))
            results.append(self.test_checkin_attendance("mentor", course_id, today, False))  # Should fail
            results.append(self.test_checkin_attendance("admin", course_id, today, False))  # Should fail
            
            # Test 2: Student Check-out
            print("\n🚪 Testing Student Check-out...")
            results.append(self.test_checkout_attendance("student", course_id, today, True))
            results.append(self.test_checkout_attendance("mentor", course_id, today, False))  # Should fail
            
            # Test 3: Get Attendance Records
            print("\n📋 Testing Get Attendance Records...")
            results.append(self.test_get_attendance_records("student", course_id, True))
            results.append(self.test_get_attendance_records("mentor", course_id, True))
            results.append(self.test_get_attendance_records("admin", course_id, True))
        
        return results

    # ==================== MATERIALS MANAGEMENT TESTS ====================
    
    def test_upload_material(self, role: str, material_data: Dict, should_succeed: bool = True) -> bool:
        """Test uploading learning material"""
        print(f"🔍 Testing Upload Material - {role.title()} User...")
        
        if role not in self.tokens:
            self.log_test(f"Upload Material {role.title()}", False, f"No {role} token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        success, response, error = self.make_request("POST", "/materials", material_data, headers)
        
        if not success:
            self.log_test(f"Upload Material {role.title()}", False, f"Request failed: {error}")
            return False
            
        if should_succeed:
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data.get("title") == material_data["title"]:
                    # Store material for later tests
                    if not hasattr(self, 'materials'):
                        self.materials = {}
                    self.materials[f"{role}_material"] = data
                    self.log_test(f"Upload Material {role.title()}", True, f"Material uploaded successfully. ID: {data['id']}")
                    return True
                else:
                    self.log_test(f"Upload Material {role.title()}", False, f"Invalid response data: {data}")
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log_test(f"Upload Material {role.title()}", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                except:
                    self.log_test(f"Upload Material {role.title()}", False, f"Status {response.status_code}: {response.text}")
                return False
        else:
            if response.status_code == 403:
                self.log_test(f"Upload Material {role.title()}", True, "Correctly rejected unauthorized upload")
                return True
            else:
                self.log_test(f"Upload Material {role.title()}", False, f"Expected 403, got {response.status_code}")
                return False
    
    def test_get_materials(self, role: str, course_id: str = None, should_succeed: bool = True) -> bool:
        """Test getting learning materials"""
        print(f"🔍 Testing Get Materials - {role.title()} User...")
        
        if role not in self.tokens:
            self.log_test(f"Get Materials {role.title()}", False, f"No {role} token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        endpoint = "/materials"
        if course_id:
            endpoint += f"?course_id={course_id}"
        success, response, error = self.make_request("GET", endpoint, headers=headers)
        
        if not success:
            self.log_test(f"Get Materials {role.title()}", False, f"Request failed: {error}")
            return False
            
        if should_succeed:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test(f"Get Materials {role.title()}", True, f"Retrieved {len(data)} materials")
                    return True
                else:
                    self.log_test(f"Get Materials {role.title()}", False, f"Expected list, got: {type(data)}")
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log_test(f"Get Materials {role.title()}", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                except:
                    self.log_test(f"Get Materials {role.title()}", False, f"Status {response.status_code}: {response.text}")
                return False
        else:
            if response.status_code == 403:
                self.log_test(f"Get Materials {role.title()}", True, "Correctly rejected unauthorized access")
                return True
            else:
                self.log_test(f"Get Materials {role.title()}", False, f"Expected 403, got {response.status_code}")
                return False

    def run_materials_tests(self):
        """Run comprehensive materials management tests"""
        print("\n" + "=" * 60)
        print("📚 MATERIALS MANAGEMENT TESTING")
        print("=" * 60)
        
        results = []
        
        # Test 1: Upload Material
        print("\n📤 Testing Material Upload...")
        if "mentor_course" in self.courses:
            course_id = self.courses["mentor_course"]["id"]
            material_data = {
                "course_id": course_id,
                "title": "Python Programming Guide",
                "description": "Comprehensive guide to Python programming",
                "file_url": "https://example.com/python-guide.pdf",
                "material_type": "document"
            }
            results.append(self.test_upload_material("mentor", material_data, True))
            results.append(self.test_upload_material("admin", material_data, True))
            results.append(self.test_upload_material("student", material_data, False))  # Should fail
        
        # Test 2: Get Materials
        print("\n📋 Testing Get Materials...")
        if "mentor_course" in self.courses:
            course_id = self.courses["mentor_course"]["id"]
            results.append(self.test_get_materials("student", course_id, True))
            results.append(self.test_get_materials("mentor", course_id, True))
            results.append(self.test_get_materials("admin", course_id, True))
        
        return results

    # ==================== CERTIFICATE GENERATION TESTS ====================
    
    def test_generate_certificate(self, role: str, cert_data: Dict, should_succeed: bool = True) -> bool:
        """Test generating certificate for student"""
        print(f"🔍 Testing Generate Certificate - {role.title()} User...")
        
        if role not in self.tokens:
            self.log_test(f"Generate Certificate {role.title()}", False, f"No {role} token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        success, response, error = self.make_request("POST", "/certificates/generate", cert_data, headers)
        
        if not success:
            self.log_test(f"Generate Certificate {role.title()}", False, f"Request failed: {error}")
            return False
            
        if should_succeed:
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data.get("student_id") == cert_data["student_id"]:
                    # Store certificate for later tests
                    if not hasattr(self, 'certificates'):
                        self.certificates = {}
                    self.certificates[f"{role}_certificate"] = data
                    self.log_test(f"Generate Certificate {role.title()}", True, f"Certificate generated successfully. ID: {data['id']}")
                    return True
                else:
                    self.log_test(f"Generate Certificate {role.title()}", False, f"Invalid response data: {data}")
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log_test(f"Generate Certificate {role.title()}", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                except:
                    self.log_test(f"Generate Certificate {role.title()}", False, f"Status {response.status_code}: {response.text}")
                return False
        else:
            if response.status_code in [403, 400]:
                self.log_test(f"Generate Certificate {role.title()}", True, "Correctly rejected unauthorized certificate generation")
                return True
            else:
                self.log_test(f"Generate Certificate {role.title()}", False, f"Expected 403/400, got {response.status_code}")
                return False
    
    def test_get_certificates(self, role: str, student_id: str = None, should_succeed: bool = True) -> bool:
        """Test getting certificates"""
        print(f"🔍 Testing Get Certificates - {role.title()} User...")
        
        if role not in self.tokens:
            self.log_test(f"Get Certificates {role.title()}", False, f"No {role} token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        endpoint = "/certificates"
        if student_id:
            endpoint += f"?student_id={student_id}"
        success, response, error = self.make_request("GET", endpoint, headers=headers)
        
        if not success:
            self.log_test(f"Get Certificates {role.title()}", False, f"Request failed: {error}")
            return False
            
        if should_succeed:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test(f"Get Certificates {role.title()}", True, f"Retrieved {len(data)} certificates")
                    return True
                else:
                    self.log_test(f"Get Certificates {role.title()}", False, f"Expected list, got: {type(data)}")
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log_test(f"Get Certificates {role.title()}", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                except:
                    self.log_test(f"Get Certificates {role.title()}", False, f"Status {response.status_code}: {response.text}")
                return False
        else:
            if response.status_code == 403:
                self.log_test(f"Get Certificates {role.title()}", True, "Correctly rejected unauthorized access")
                return True
            else:
                self.log_test(f"Get Certificates {role.title()}", False, f"Expected 403, got {response.status_code}")
                return False

    def run_certificate_tests(self):
        """Run comprehensive certificate generation tests"""
        print("\n" + "=" * 60)
        print("🏆 CERTIFICATE GENERATION TESTING")
        print("=" * 60)
        
        results = []
        
        # First, ensure student enrollment is completed
        if "mentor_course" in self.courses and "student" in self.users:
            course_id = self.courses["mentor_course"]["id"]
            student_id = self.users["student"]["id"]
            
            # Update enrollment status to completed (prerequisite for certificate generation)
            if "admin" in self.tokens:
                headers = {"Authorization": f"Bearer {self.tokens['admin']}"}
                status_data = {"completion_status": "completed"}
                self.make_request("PUT", f"/enrollments/{course_id}/student/{student_id}/status", status_data, headers)
        
        # Test 1: Generate Certificate
        print("\n🏆 Testing Certificate Generation...")
        if "mentor_course" in self.courses and "student" in self.users:
            course_id = self.courses["mentor_course"]["id"]
            student_id = self.users["student"]["id"]
            cert_data = {
                "course_id": course_id,
                "student_id": student_id,
                "completion_date": "2025-01-01T00:00:00Z"
            }
            results.append(self.test_generate_certificate("mentor", cert_data, True))
            results.append(self.test_generate_certificate("admin", cert_data, False))  # Should fail (already exists)
            results.append(self.test_generate_certificate("student", cert_data, False))  # Should fail
        
        # Test 2: Get Certificates
        print("\n📋 Testing Get Certificates...")
        results.append(self.test_get_certificates("student", None, True))
        results.append(self.test_get_certificates("mentor", None, True))
        results.append(self.test_get_certificates("admin", None, True))
        
        return results

    # ==================== FEE REMINDER TESTS ====================
    
    def test_create_fee_reminder(self, role: str, fee_data: Dict, should_succeed: bool = True) -> bool:
        """Test creating fee reminder"""
        print(f"🔍 Testing Create Fee Reminder - {role.title()} User...")
        
        if role not in self.tokens:
            self.log_test(f"Create Fee Reminder {role.title()}", False, f"No {role} token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        success, response, error = self.make_request("POST", "/fee-reminders", fee_data, headers)
        
        if not success:
            self.log_test(f"Create Fee Reminder {role.title()}", False, f"Request failed: {error}")
            return False
            
        if should_succeed:
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data.get("student_id") == fee_data["student_id"]:
                    # Store fee reminder for later tests
                    if not hasattr(self, 'fee_reminders'):
                        self.fee_reminders = {}
                    self.fee_reminders[f"{role}_fee_reminder"] = data
                    self.log_test(f"Create Fee Reminder {role.title()}", True, f"Fee reminder created successfully. ID: {data['id']}")
                    return True
                else:
                    self.log_test(f"Create Fee Reminder {role.title()}", False, f"Invalid response data: {data}")
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log_test(f"Create Fee Reminder {role.title()}", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                except:
                    self.log_test(f"Create Fee Reminder {role.title()}", False, f"Status {response.status_code}: {response.text}")
                return False
        else:
            if response.status_code == 403:
                self.log_test(f"Create Fee Reminder {role.title()}", True, "Correctly rejected unauthorized fee reminder creation")
                return True
            else:
                self.log_test(f"Create Fee Reminder {role.title()}", False, f"Expected 403, got {response.status_code}")
                return False
    
    def test_get_fee_reminders(self, role: str, student_id: str = None, should_succeed: bool = True) -> bool:
        """Test getting fee reminders"""
        print(f"🔍 Testing Get Fee Reminders - {role.title()} User...")
        
        if role not in self.tokens:
            self.log_test(f"Get Fee Reminders {role.title()}", False, f"No {role} token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        endpoint = "/fee-reminders"
        if student_id:
            endpoint += f"?student_id={student_id}"
        success, response, error = self.make_request("GET", endpoint, headers=headers)
        
        if not success:
            self.log_test(f"Get Fee Reminders {role.title()}", False, f"Request failed: {error}")
            return False
            
        if should_succeed:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test(f"Get Fee Reminders {role.title()}", True, f"Retrieved {len(data)} fee reminders")
                    return True
                else:
                    self.log_test(f"Get Fee Reminders {role.title()}", False, f"Expected list, got: {type(data)}")
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log_test(f"Get Fee Reminders {role.title()}", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                except:
                    self.log_test(f"Get Fee Reminders {role.title()}", False, f"Status {response.status_code}: {response.text}")
                return False
        else:
            if response.status_code == 403:
                self.log_test(f"Get Fee Reminders {role.title()}", True, "Correctly rejected unauthorized access")
                return True
            else:
                self.log_test(f"Get Fee Reminders {role.title()}", False, f"Expected 403, got {response.status_code}")
                return False

    def run_fee_reminder_tests(self):
        """Run comprehensive fee reminder tests"""
        print("\n" + "=" * 60)
        print("💰 FEE REMINDER SYSTEM TESTING")
        print("=" * 60)
        
        results = []
        
        # Test 1: Create Fee Reminder
        print("\n💰 Testing Fee Reminder Creation...")
        if "student" in self.users:
            student_id = self.users["student"]["id"]
            fee_data = {
                "student_id": student_id,
                "amount": 1500.00,
                "due_date": "2025-02-15",
                "description": "Course fee payment due"
            }
            results.append(self.test_create_fee_reminder("admin", fee_data, True))
            results.append(self.test_create_fee_reminder("mentor", fee_data, False))  # Should fail
            results.append(self.test_create_fee_reminder("student", fee_data, False))  # Should fail
        
        # Test 2: Get Fee Reminders
        print("\n📋 Testing Get Fee Reminders...")
        results.append(self.test_get_fee_reminders("student", None, True))
        results.append(self.test_get_fee_reminders("admin", None, True))
        results.append(self.test_get_fee_reminders("mentor", None, False))  # Should fail
        
        return results

    # ==================== MOCK INTERVIEW TESTS ====================
    
    def test_schedule_mock_interview(self, role: str, interview_data: Dict, should_succeed: bool = True) -> bool:
        """Test scheduling mock interview"""
        print(f"🔍 Testing Schedule Mock Interview - {role.title()} User...")
        
        if role not in self.tokens:
            self.log_test(f"Schedule Mock Interview {role.title()}", False, f"No {role} token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        success, response, error = self.make_request("POST", "/mock-interviews", interview_data, headers)
        
        if not success:
            self.log_test(f"Schedule Mock Interview {role.title()}", False, f"Request failed: {error}")
            return False
            
        if should_succeed:
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data.get("student_id") == interview_data["student_id"]:
                    # Store interview for later tests
                    if not hasattr(self, 'interviews'):
                        self.interviews = {}
                    self.interviews[f"{role}_interview"] = data
                    self.log_test(f"Schedule Mock Interview {role.title()}", True, f"Interview scheduled successfully. ID: {data['id']}")
                    return True
                else:
                    self.log_test(f"Schedule Mock Interview {role.title()}", False, f"Invalid response data: {data}")
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log_test(f"Schedule Mock Interview {role.title()}", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                except:
                    self.log_test(f"Schedule Mock Interview {role.title()}", False, f"Status {response.status_code}: {response.text}")
                return False
        else:
            if response.status_code == 403:
                self.log_test(f"Schedule Mock Interview {role.title()}", True, "Correctly rejected unauthorized interview scheduling")
                return True
            else:
                self.log_test(f"Schedule Mock Interview {role.title()}", False, f"Expected 403, got {response.status_code}")
                return False
    
    def test_get_mock_interviews(self, role: str, student_id: str = None, should_succeed: bool = True) -> bool:
        """Test getting mock interviews"""
        print(f"🔍 Testing Get Mock Interviews - {role.title()} User...")
        
        if role not in self.tokens:
            self.log_test(f"Get Mock Interviews {role.title()}", False, f"No {role} token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        endpoint = "/mock-interviews"
        if student_id:
            endpoint += f"?student_id={student_id}"
        success, response, error = self.make_request("GET", endpoint, headers=headers)
        
        if not success:
            self.log_test(f"Get Mock Interviews {role.title()}", False, f"Request failed: {error}")
            return False
            
        if should_succeed:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test(f"Get Mock Interviews {role.title()}", True, f"Retrieved {len(data)} mock interviews")
                    return True
                else:
                    self.log_test(f"Get Mock Interviews {role.title()}", False, f"Expected list, got: {type(data)}")
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log_test(f"Get Mock Interviews {role.title()}", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                except:
                    self.log_test(f"Get Mock Interviews {role.title()}", False, f"Status {response.status_code}: {response.text}")
                return False
        else:
            if response.status_code == 403:
                self.log_test(f"Get Mock Interviews {role.title()}", True, "Correctly rejected unauthorized access")
                return True
            else:
                self.log_test(f"Get Mock Interviews {role.title()}", False, f"Expected 403, got {response.status_code}")
                return False

    def run_mock_interview_tests(self):
        """Run comprehensive mock interview tests"""
        print("\n" + "=" * 60)
        print("🎤 MOCK INTERVIEW SYSTEM TESTING")
        print("=" * 60)
        
        results = []
        
        # Test 1: Schedule Mock Interview
        print("\n🎤 Testing Mock Interview Scheduling...")
        if "student" in self.users and "mentor" in self.users:
            student_id = self.users["student"]["id"]
            mentor_id = self.users["mentor"]["id"]
            interview_data = {
                "student_id": student_id,
                "mentor_id": mentor_id,
                "scheduled_date": "2025-02-01T10:00:00Z",
                "type": "technical",
                "duration": 60
            }
            results.append(self.test_schedule_mock_interview("admin", interview_data, True))
            results.append(self.test_schedule_mock_interview("mentor", interview_data, True))
            results.append(self.test_schedule_mock_interview("student", interview_data, False))  # Should fail
        
        # Test 2: Get Mock Interviews
        print("\n📋 Testing Get Mock Interviews...")
        results.append(self.test_get_mock_interviews("student", None, True))
        results.append(self.test_get_mock_interviews("mentor", None, True))
        results.append(self.test_get_mock_interviews("admin", None, True))
        
        return results

    # ==================== PROGRESS REPORTING TESTS ====================
    
    def test_get_progress_report(self, role: str, endpoint: str, should_succeed: bool = True) -> bool:
        """Test getting progress reports"""
        print(f"🔍 Testing Get Progress Report - {role.title()} User...")
        
        if role not in self.tokens:
            self.log_test(f"Get Progress Report {role.title()}", False, f"No {role} token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        success, response, error = self.make_request("GET", endpoint, headers=headers)
        
        if not success:
            self.log_test(f"Get Progress Report {role.title()}", False, f"Request failed: {error}")
            return False
            
        if should_succeed:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, (dict, list)):
                    self.log_test(f"Get Progress Report {role.title()}", True, f"Retrieved progress report data")
                    return True
                else:
                    self.log_test(f"Get Progress Report {role.title()}", False, f"Expected dict/list, got: {type(data)}")
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log_test(f"Get Progress Report {role.title()}", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                except:
                    self.log_test(f"Get Progress Report {role.title()}", False, f"Status {response.status_code}: {response.text}")
                return False
        else:
            if response.status_code == 403:
                self.log_test(f"Get Progress Report {role.title()}", True, "Correctly rejected unauthorized access")
                return True
            else:
                self.log_test(f"Get Progress Report {role.title()}", False, f"Expected 403, got {response.status_code}")
                return False

    def run_progress_reporting_tests(self):
        """Run comprehensive progress reporting tests"""
        print("\n" + "=" * 60)
        print("📊 PROGRESS REPORTING SYSTEM TESTING")
        print("=" * 60)
        
        results = []
        
        # Test 1: Overall Progress Report
        print("\n📊 Testing Overall Progress Report...")
        results.append(self.test_get_progress_report("admin", "/reports/progress", True))
        results.append(self.test_get_progress_report("mentor", "/reports/progress", True))
        results.append(self.test_get_progress_report("student", "/reports/progress", False))  # Should fail
        
        # Test 2: Student Progress Report
        print("\n👨‍🎓 Testing Student Progress Report...")
        if "student" in self.users:
            student_id = self.users["student"]["id"]
            results.append(self.test_get_progress_report("admin", f"/reports/student/{student_id}/progress", True))
            results.append(self.test_get_progress_report("mentor", f"/reports/student/{student_id}/progress", True))
            results.append(self.test_get_progress_report("student", f"/reports/student/{student_id}/progress", False))  # Should fail
        
        # Test 3: Course Progress Report
        print("\n🎓 Testing Course Progress Report...")
        if "mentor_course" in self.courses:
            course_id = self.courses["mentor_course"]["id"]
            results.append(self.test_get_progress_report("admin", f"/reports/course/{course_id}/progress", True))
            results.append(self.test_get_progress_report("mentor", f"/reports/course/{course_id}/progress", True))
            results.append(self.test_get_progress_report("student", f"/reports/course/{course_id}/progress", False))  # Should fail
        
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
        
        # Test 10: Enrollment Management Tests
        enrollment_results = self.run_enrollment_tests()
        results.extend(enrollment_results)
        
        # Test 11: Task/Assignment Management Tests
        task_results = self.run_task_management_tests()
        results.extend(task_results)
        
        # Test 12: Attendance Tracking System Tests
        attendance_results = self.run_attendance_tests()
        results.extend(attendance_results)
        
        # Test 13: Materials Management System Tests
        materials_results = self.run_materials_tests()
        results.extend(materials_results)
        
        # Test 14: Certificate Generation System Tests
        certificate_results = self.run_certificate_tests()
        results.extend(certificate_results)
        
        # Test 15: Fee Reminder System Tests
        fee_reminder_results = self.run_fee_reminder_tests()
        results.extend(fee_reminder_results)
        
        # Test 16: Mock Interview System Tests
        interview_results = self.run_mock_interview_tests()
        results.extend(interview_results)
        
        # Test 17: Progress Reporting System Tests
        progress_results = self.run_progress_reporting_tests()
        results.extend(progress_results)
        
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
            print("✅ Enrollment management system: WORKING")
            print("✅ Task/assignment management system: WORKING")
            print("✅ Attendance tracking system: WORKING")
            print("✅ Materials management system: WORKING")
            print("✅ Certificate generation system: WORKING")
            print("✅ Fee reminder system: WORKING")
            print("✅ Mock interview system: WORKING")
            print("✅ Progress reporting system: WORKING")
            return True
        else:
            print(f"\n⚠️  {total - passed} test(s) failed. Please check the issues above.")
            return False

if __name__ == "__main__":
    tester = LMSAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)