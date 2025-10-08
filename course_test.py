#!/usr/bin/env python3
"""
Course Management Testing with Existing Users
Tests course operations using existing user data
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

# Get backend URL from supervisor configuration
BACKEND_URL = "https://auth-creds-update.preview.emergentagent.com/api"

class CourseAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        
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
    
    def create_test_token(self, user_id: str, role: str) -> str:
        """Create a test JWT token for existing user"""
        try:
            import jwt
            from datetime import datetime, timedelta, timezone
            
            # Use the same secret as the backend
            SECRET_KEY = 'your-secret-key-change-in-production'  # Default from backend
            ALGORITHM = "HS256"
            
            # Create token payload
            payload = {
                "sub": user_id,
                "role": role,
                "exp": datetime.now(timezone.utc) + timedelta(hours=24)
            }
            
            # Generate token
            token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
            return token
            
        except Exception as e:
            print(f"Error creating token: {e}")
            return None
    
    def get_existing_users(self):
        """Get existing users from database"""
        try:
            import os
            from dotenv import load_dotenv
            from supabase import create_client
            
            # Load environment variables
            load_dotenv('/app/backend/.env')
            url = os.environ.get('SUPABASE_URL')
            key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
            
            # Create Supabase client
            supabase = create_client(url, key)
            
            # Query users
            result = supabase.table("users").select("id, username, role").execute()
            
            if result.data:
                return result.data
            else:
                return []
                
        except Exception as e:
            print(f"Error getting users: {e}")
            return []
    
    def test_course_operations(self):
        """Test course operations with existing users"""
        print("🔍 Testing Course Operations...")
        
        # Get existing users
        users = self.get_existing_users()
        if not users:
            self.log_test("Course Operations", False, "No existing users found")
            return False
        
        print(f"   Found {len(users)} existing users:")
        for user in users:
            print(f"     - {user['username']} ({user['role']})")
        
        # Find admin and mentor users
        admin_user = next((u for u in users if u['role'] == 'admin'), None)
        mentor_user = next((u for u in users if u['role'] == 'mentor'), None)
        student_user = next((u for u in users if u['role'] == 'student'), None)
        
        if not admin_user:
            self.log_test("Course Operations", False, "No admin user found")
            return False
        
        # Create tokens for testing
        admin_token = self.create_test_token(admin_user['id'], admin_user['role'])
        if not admin_token:
            self.log_test("Course Operations", False, "Failed to create admin token")
            return False
        
        print(f"   Created token for admin user: {admin_user['username']}")
        
        # Test 1: List courses (should work even with empty list)
        print("   Testing course listing...")
        headers = {"Authorization": f"Bearer {admin_token}"}
        success, response, error = self.make_request("GET", "/courses", headers=headers)
        
        if not success:
            self.log_test("Course Operations", False, f"Course listing failed: {error}")
            return False
        
        if response.status_code == 200:
            courses = response.json()
            print(f"     ✅ Course listing successful: {len(courses)} courses found")
        else:
            self.log_test("Course Operations", False, f"Course listing failed with status {response.status_code}")
            return False
        
        # Test 2: Create a course
        print("   Testing course creation...")
        course_data = {
            "title": "Test Course - Supabase Connection",
            "description": "A test course to verify Supabase connection and course management",
            "mentor_id": mentor_user['id'] if mentor_user else admin_user['id']
        }
        
        success, response, error = self.make_request("POST", "/courses", course_data, headers)
        
        if not success:
            self.log_test("Course Operations", False, f"Course creation failed: {error}")
            return False
        
        if response.status_code == 200:
            created_course = response.json()
            course_id = created_course.get('id')
            print(f"     ✅ Course creation successful: {created_course.get('title')} (ID: {course_id})")
            
            # Test 3: Get the created course
            print("   Testing single course retrieval...")
            success, response, error = self.make_request("GET", f"/courses/{course_id}", headers=headers)
            
            if success and response.status_code == 200:
                retrieved_course = response.json()
                print(f"     ✅ Course retrieval successful: {retrieved_course.get('title')}")
            else:
                print(f"     ❌ Course retrieval failed")
            
            # Test 4: Update the course
            print("   Testing course update...")
            update_data = {
                "title": "Updated Test Course - Supabase Connection Verified",
                "description": "Updated description to verify course update functionality"
            }
            
            success, response, error = self.make_request("PUT", f"/courses/{course_id}", update_data, headers)
            
            if success and response.status_code == 200:
                updated_course = response.json()
                print(f"     ✅ Course update successful: {updated_course.get('title')}")
            else:
                print(f"     ❌ Course update failed")
            
            # Test 5: Approve the course
            print("   Testing course approval...")
            approval_data = {"approval_status": "approved"}
            
            success, response, error = self.make_request("PUT", f"/courses/{course_id}/approve", approval_data, headers)
            
            if success and response.status_code == 200:
                approved_course = response.json()
                print(f"     ✅ Course approval successful: {approved_course.get('approval_status')}")
            else:
                print(f"     ❌ Course approval failed")
            
            # Test 6: Clean up - delete the test course
            print("   Cleaning up test course...")
            success, response, error = self.make_request("DELETE", f"/courses/{course_id}", headers=headers)
            
            if success and response.status_code == 200:
                print(f"     ✅ Test course deleted successfully")
            else:
                print(f"     ❌ Test course deletion failed")
            
            self.log_test("Course Operations", True, "All course operations completed successfully")
            return True
            
        else:
            try:
                error_data = response.json()
                self.log_test("Course Operations", False, f"Course creation failed: {error_data.get('detail', 'Unknown error')}")
            except:
                self.log_test("Course Operations", False, f"Course creation failed with status {response.status_code}")
            return False
    
    def test_user_management(self):
        """Test user management endpoints"""
        print("🔍 Testing User Management...")
        
        # Get existing users
        users = self.get_existing_users()
        if not users:
            self.log_test("User Management", False, "No existing users found")
            return False
        
        admin_user = next((u for u in users if u['role'] == 'admin'), None)
        if not admin_user:
            self.log_test("User Management", False, "No admin user found")
            return False
        
        # Create admin token
        admin_token = self.create_test_token(admin_user['id'], admin_user['role'])
        if not admin_token:
            self.log_test("User Management", False, "Failed to create admin token")
            return False
        
        # Test getting all users
        headers = {"Authorization": f"Bearer {admin_token}"}
        success, response, error = self.make_request("GET", "/users", headers=headers)
        
        if not success:
            self.log_test("User Management", False, f"Get users failed: {error}")
            return False
        
        if response.status_code == 200:
            users_list = response.json()
            self.log_test("User Management", True, f"Successfully retrieved {len(users_list)} users")
            return True
        else:
            self.log_test("User Management", False, f"Get users failed with status {response.status_code}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("=" * 60)
        print("🎓 Course Management Testing Suite")
        print("=" * 60)
        
        results = []
        
        # Test 1: Course Operations
        results.append(self.test_course_operations())
        
        # Test 2: User Management
        results.append(self.test_user_management())
        
        # Summary
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(results)
        total = len(results)
        
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        if passed == total:
            print("\n🎉 All course management tests passed!")
        else:
            print(f"\n⚠️  {total - passed} test(s) failed.")
        
        return results

if __name__ == "__main__":
    tester = CourseAPITester()
    results = tester.run_all_tests()
    
    # Exit with error code if any tests failed
    if not all(results):
        sys.exit(1)