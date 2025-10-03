#!/usr/bin/env python3
"""
LMS Missing Features Detection Test
Tests for missing LMS functionality that should be implemented
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

# Get backend URL from frontend .env
BACKEND_URL = "https://mentor-dash-fix.preview.emergentagent.com/api"

class MissingFeaturesDetector:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.admin_token = None
        self.mentor_token = None
        self.student_token = None
        self.test_user_ids = {}
        self.test_course_id = None
        
    def log_test(self, feature_name: str, exists: bool, message: str = ""):
        status = "✅ IMPLEMENTED" if exists else "❌ MISSING"
        print(f"{status} {feature_name}")
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
    
    def setup_test_environment(self):
        """Create test users and get tokens"""
        print("🔧 Setting up test environment...")
        
        import time
        timestamp = str(int(time.time()))
        
        # Register test users
        test_users = [
            ("admin", f"test_admin_missing_{timestamp}", f"test_admin_missing_{timestamp}@test.com", "Test Admin", "admin123"),
            ("mentor", f"test_mentor_missing_{timestamp}", f"test_mentor_missing_{timestamp}@test.com", "Test Mentor", "mentor123"),
            ("student", f"test_student_missing_{timestamp}", f"test_student_missing_{timestamp}@test.com", "Test Student", "student123")
        ]
        
        for role, username, email, full_name, password in test_users:
            user_data = {
                "username": username,
                "email": email,
                "password": password,
                "full_name": full_name,
                "role": role
            }
            
            success, response, error = self.make_request("POST", "/auth/register", user_data)
            if success and response.status_code == 200:
                data = response.json()
                if role == "admin":
                    self.admin_token = data["access_token"]
                    self.test_user_ids["admin"] = data["user"]["id"]
                elif role == "mentor":
                    self.mentor_token = data["access_token"]
                    self.test_user_ids["mentor"] = data["user"]["id"]
                elif role == "student":
                    self.student_token = data["access_token"]
                    self.test_user_ids["student"] = data["user"]["id"]
                print(f"✅ Created {role} user")
            else:
                print(f"❌ Failed to create {role} user")
                return False
        
        # Create a test course for enrollment tests
        if self.admin_token:
            course_data = {
                "title": "Test Course for Missing Features",
                "description": "Course for testing missing LMS features",
                "mentor_id": self.test_user_ids["mentor"]
            }
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            success, response, error = self.make_request("POST", "/courses", course_data, headers)
            if success and response.status_code == 200:
                self.test_course_id = response.json()["id"]
                print("✅ Created test course")
            else:
                print("❌ Failed to create test course")
        
        print("🔧 Test environment setup complete\n")
        return True
    
    def test_enrollment_management(self):
        """Test enrollment management endpoints"""
        print("🎓 Testing Enrollment Management System...")
        
        missing_endpoints = []
        
        # Test enrollment endpoints
        enrollment_endpoints = [
            ("POST", "/enrollments", "Student course enrollment"),
            ("GET", "/enrollments", "List user enrollments"),
            ("GET", f"/enrollments/student/{self.test_user_ids.get('student', 'test')}", "Get student enrollments"),
            ("GET", f"/enrollments/course/{self.test_course_id or 'test'}", "Get course enrollments"),
            ("DELETE", f"/enrollments/{self.test_course_id or 'test'}/student/{self.test_user_ids.get('student', 'test')}", "Unenroll student"),
            ("PUT", f"/enrollments/{self.test_course_id or 'test'}/student/{self.test_user_ids.get('student', 'test')}/status", "Update enrollment status")
        ]
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        for method, endpoint, description in enrollment_endpoints:
            success, response, error = self.make_request(method, endpoint, {}, headers)
            
            if not success:
                missing_endpoints.append(description)
                self.log_test(description, False, f"Endpoint not accessible: {error}")
            elif response.status_code == 404:
                missing_endpoints.append(description)
                self.log_test(description, False, "Endpoint not found (404)")
            elif response.status_code in [200, 201, 400, 403]:  # 400/403 means endpoint exists but may have validation issues
                self.log_test(description, True, f"Endpoint exists (Status: {response.status_code})")
            else:
                missing_endpoints.append(description)
                self.log_test(description, False, f"Unexpected status: {response.status_code}")
        
        return len(missing_endpoints) == 0
    
    def test_task_assignment_system(self):
        """Test task/assignment management endpoints"""
        print("📝 Testing Task/Assignment System...")
        
        missing_endpoints = []
        
        # Test task management endpoints
        task_endpoints = [
            ("POST", "/tasks", "Create task/assignment"),
            ("GET", "/tasks", "List all tasks"),
            ("GET", f"/tasks/course/{self.test_course_id or 'test'}", "Get course tasks"),
            ("GET", "/tasks/123", "Get single task"),
            ("PUT", "/tasks/123", "Update task"),
            ("DELETE", "/tasks/123", "Delete task"),
            ("POST", "/tasks/123/submissions", "Submit task"),
            ("GET", "/tasks/123/submissions", "Get task submissions"),
            ("PUT", "/tasks/123/submissions/456/grade", "Grade submission"),
            ("GET", f"/tasks/student/{self.test_user_ids.get('student', 'test')}", "Get student tasks")
        ]
        
        headers = {"Authorization": f"Bearer {self.mentor_token}"}
        
        for method, endpoint, description in task_endpoints:
            success, response, error = self.make_request(method, endpoint, {}, headers)
            
            if not success:
                missing_endpoints.append(description)
                self.log_test(description, False, f"Endpoint not accessible: {error}")
            elif response.status_code == 404:
                missing_endpoints.append(description)
                self.log_test(description, False, "Endpoint not found (404)")
            elif response.status_code in [200, 201, 400, 403]:
                self.log_test(description, True, f"Endpoint exists (Status: {response.status_code})")
            else:
                missing_endpoints.append(description)
                self.log_test(description, False, f"Unexpected status: {response.status_code}")
        
        return len(missing_endpoints) == 0
    
    def test_attendance_tracking(self):
        """Test attendance tracking endpoints"""
        print("📅 Testing Attendance Tracking System...")
        
        missing_endpoints = []
        
        # Test attendance endpoints
        attendance_endpoints = [
            ("POST", "/attendance/checkin", "Student check-in"),
            ("POST", "/attendance/checkout", "Student check-out"),
            ("GET", "/attendance", "List attendance records"),
            ("GET", f"/attendance/student/{self.test_user_ids.get('student', 'test')}", "Get student attendance"),
            ("GET", f"/attendance/course/{self.test_course_id or 'test'}", "Get course attendance"),
            ("PUT", "/attendance/123", "Update attendance record"),
            ("GET", "/attendance/reports", "Attendance reports"),
            ("POST", "/attendance/bulk", "Bulk attendance update")
        ]
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        for method, endpoint, description in attendance_endpoints:
            success, response, error = self.make_request(method, endpoint, {}, headers)
            
            if not success:
                missing_endpoints.append(description)
                self.log_test(description, False, f"Endpoint not accessible: {error}")
            elif response.status_code == 404:
                missing_endpoints.append(description)
                self.log_test(description, False, "Endpoint not found (404)")
            elif response.status_code in [200, 201, 400, 403]:
                self.log_test(description, True, f"Endpoint exists (Status: {response.status_code})")
            else:
                missing_endpoints.append(description)
                self.log_test(description, False, f"Unexpected status: {response.status_code}")
        
        return len(missing_endpoints) == 0
    
    def test_materials_management(self):
        """Test materials management endpoints"""
        print("📚 Testing Materials Management System...")
        
        missing_endpoints = []
        
        # Test materials endpoints
        materials_endpoints = [
            ("POST", "/materials", "Upload material"),
            ("GET", "/materials", "List all materials"),
            ("GET", f"/materials/course/{self.test_course_id or 'test'}", "Get course materials"),
            ("GET", "/materials/123", "Get single material"),
            ("PUT", "/materials/123", "Update material"),
            ("DELETE", "/materials/123", "Delete material"),
            ("GET", "/materials/123/download", "Download material"),
            ("POST", "/materials/123/share", "Share material")
        ]
        
        headers = {"Authorization": f"Bearer {self.mentor_token}"}
        
        for method, endpoint, description in materials_endpoints:
            success, response, error = self.make_request(method, endpoint, {}, headers)
            
            if not success:
                missing_endpoints.append(description)
                self.log_test(description, False, f"Endpoint not accessible: {error}")
            elif response.status_code == 404:
                missing_endpoints.append(description)
                self.log_test(description, False, "Endpoint not found (404)")
            elif response.status_code in [200, 201, 400, 403]:
                self.log_test(description, True, f"Endpoint exists (Status: {response.status_code})")
            else:
                missing_endpoints.append(description)
                self.log_test(description, False, f"Unexpected status: {response.status_code}")
        
        return len(missing_endpoints) == 0
    
    def test_certificate_generation(self):
        """Test certificate generation endpoints"""
        print("🏆 Testing Certificate Generation System...")
        
        missing_endpoints = []
        
        # Test certificate endpoints
        certificate_endpoints = [
            ("POST", "/certificates/generate", "Generate certificate"),
            ("GET", "/certificates", "List certificates"),
            ("GET", f"/certificates/student/{self.test_user_ids.get('student', 'test')}", "Get student certificates"),
            ("GET", "/certificates/123", "Get single certificate"),
            ("GET", "/certificates/123/download", "Download certificate"),
            ("PUT", "/certificates/123", "Update certificate"),
            ("POST", "/certificates/123/send", "Send certificate via email")
        ]
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        for method, endpoint, description in certificate_endpoints:
            success, response, error = self.make_request(method, endpoint, {}, headers)
            
            if not success:
                missing_endpoints.append(description)
                self.log_test(description, False, f"Endpoint not accessible: {error}")
            elif response.status_code == 404:
                missing_endpoints.append(description)
                self.log_test(description, False, "Endpoint not found (404)")
            elif response.status_code in [200, 201, 400, 403]:
                self.log_test(description, True, f"Endpoint exists (Status: {response.status_code})")
            else:
                missing_endpoints.append(description)
                self.log_test(description, False, f"Unexpected status: {response.status_code}")
        
        return len(missing_endpoints) == 0
    
    def test_fee_reminder_system(self):
        """Test fee reminder system endpoints"""
        print("💰 Testing Fee Reminder System...")
        
        missing_endpoints = []
        
        # Test fee reminder endpoints
        fee_endpoints = [
            ("POST", "/fee-reminders", "Create fee reminder"),
            ("GET", "/fee-reminders", "List fee reminders"),
            ("GET", f"/fee-reminders/student/{self.test_user_ids.get('student', 'test')}", "Get student fee reminders"),
            ("PUT", "/fee-reminders/123", "Update fee reminder"),
            ("DELETE", "/fee-reminders/123", "Delete fee reminder"),
            ("POST", "/fee-reminders/123/send", "Send fee reminder"),
            ("PUT", "/fee-reminders/123/paid", "Mark as paid")
        ]
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        for method, endpoint, description in fee_endpoints:
            success, response, error = self.make_request(method, endpoint, {}, headers)
            
            if not success:
                missing_endpoints.append(description)
                self.log_test(description, False, f"Endpoint not accessible: {error}")
            elif response.status_code == 404:
                missing_endpoints.append(description)
                self.log_test(description, False, "Endpoint not found (404)")
            elif response.status_code in [200, 201, 400, 403]:
                self.log_test(description, True, f"Endpoint exists (Status: {response.status_code})")
            else:
                missing_endpoints.append(description)
                self.log_test(description, False, f"Unexpected status: {response.status_code}")
        
        return len(missing_endpoints) == 0
    
    def test_mock_interview_scheduling(self):
        """Test mock interview scheduling endpoints"""
        print("🎤 Testing Mock Interview Scheduling System...")
        
        missing_endpoints = []
        
        # Test mock interview endpoints
        interview_endpoints = [
            ("POST", "/mock-interviews", "Schedule mock interview"),
            ("GET", "/mock-interviews", "List mock interviews"),
            ("GET", f"/mock-interviews/student/{self.test_user_ids.get('student', 'test')}", "Get student interviews"),
            ("GET", f"/mock-interviews/mentor/{self.test_user_ids.get('mentor', 'test')}", "Get mentor interviews"),
            ("PUT", "/mock-interviews/123", "Update interview"),
            ("DELETE", "/mock-interviews/123", "Cancel interview"),
            ("POST", "/mock-interviews/123/feedback", "Add interview feedback"),
            ("GET", "/mock-interviews/123/feedback", "Get interview feedback")
        ]
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        for method, endpoint, description in interview_endpoints:
            success, response, error = self.make_request(method, endpoint, {}, headers)
            
            if not success:
                missing_endpoints.append(description)
                self.log_test(description, False, f"Endpoint not accessible: {error}")
            elif response.status_code == 404:
                missing_endpoints.append(description)
                self.log_test(description, False, "Endpoint not found (404)")
            elif response.status_code in [200, 201, 400, 403]:
                self.log_test(description, True, f"Endpoint exists (Status: {response.status_code})")
            else:
                missing_endpoints.append(description)
                self.log_test(description, False, f"Unexpected status: {response.status_code}")
        
        return len(missing_endpoints) == 0
    
    def test_progress_reporting(self):
        """Test progress reporting endpoints"""
        print("📊 Testing Progress Reporting System...")
        
        missing_endpoints = []
        
        # Test progress reporting endpoints
        progress_endpoints = [
            ("GET", "/reports/progress", "Overall progress report"),
            ("GET", f"/reports/student/{self.test_user_ids.get('student', 'test')}/progress", "Student progress report"),
            ("GET", f"/reports/course/{self.test_course_id or 'test'}/progress", "Course progress report"),
            ("GET", f"/reports/mentor/{self.test_user_ids.get('mentor', 'test')}/students", "Mentor student reports"),
            ("GET", "/reports/attendance", "Attendance reports"),
            ("GET", "/reports/grades", "Grade reports"),
            ("GET", "/reports/completion", "Course completion reports"),
            ("POST", "/reports/custom", "Generate custom report")
        ]
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        for method, endpoint, description in progress_endpoints:
            success, response, error = self.make_request(method, endpoint, {}, headers)
            
            if not success:
                missing_endpoints.append(description)
                self.log_test(description, False, f"Endpoint not accessible: {error}")
            elif response.status_code == 404:
                missing_endpoints.append(description)
                self.log_test(description, False, "Endpoint not found (404)")
            elif response.status_code in [200, 201, 400, 403]:
                self.log_test(description, True, f"Endpoint exists (Status: {response.status_code})")
            else:
                missing_endpoints.append(description)
                self.log_test(description, False, f"Unexpected status: {response.status_code}")
        
        return len(missing_endpoints) == 0
    
    def test_email_notification_system(self):
        """Test email notification system endpoints"""
        print("📧 Testing Email Notification System...")
        
        missing_endpoints = []
        
        # Test email notification endpoints
        email_endpoints = [
            ("POST", "/notifications/email", "Send email notification"),
            ("GET", "/notifications", "List notifications"),
            ("POST", "/notifications/bulk", "Send bulk notifications"),
            ("GET", "/notifications/templates", "Get email templates"),
            ("POST", "/notifications/templates", "Create email template"),
            ("PUT", "/notifications/templates/123", "Update email template"),
            ("POST", "/notifications/course-reminder", "Send course reminders"),
            ("POST", "/notifications/assignment-due", "Send assignment due reminders")
        ]
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        for method, endpoint, description in email_endpoints:
            success, response, error = self.make_request(method, endpoint, {}, headers)
            
            if not success:
                missing_endpoints.append(description)
                self.log_test(description, False, f"Endpoint not accessible: {error}")
            elif response.status_code == 404:
                missing_endpoints.append(description)
                self.log_test(description, False, "Endpoint not found (404)")
            elif response.status_code in [200, 201, 400, 403]:
                self.log_test(description, True, f"Endpoint exists (Status: {response.status_code})")
            else:
                missing_endpoints.append(description)
                self.log_test(description, False, f"Unexpected status: {response.status_code}")
        
        return len(missing_endpoints) == 0
    
    def run_missing_features_detection(self):
        """Run complete missing features detection"""
        print("=" * 80)
        print("🔍 LMS MISSING FEATURES DETECTION")
        print("=" * 80)
        
        if not self.setup_test_environment():
            print("❌ Failed to setup test environment")
            return False
        
        # Test each major LMS feature category
        feature_results = {}
        
        feature_results["Enrollment Management"] = self.test_enrollment_management()
        feature_results["Task/Assignment System"] = self.test_task_assignment_system()
        feature_results["Attendance Tracking"] = self.test_attendance_tracking()
        feature_results["Materials Management"] = self.test_materials_management()
        feature_results["Certificate Generation"] = self.test_certificate_generation()
        feature_results["Fee Reminder System"] = self.test_fee_reminder_system()
        feature_results["Mock Interview Scheduling"] = self.test_mock_interview_scheduling()
        feature_results["Progress Reporting"] = self.test_progress_reporting()
        feature_results["Email Notification System"] = self.test_email_notification_system()
        
        # Summary
        print("=" * 80)
        print("📋 MISSING FEATURES SUMMARY")
        print("=" * 80)
        
        implemented_count = sum(feature_results.values())
        total_features = len(feature_results)
        missing_count = total_features - implemented_count
        
        print(f"✅ Implemented Features: {implemented_count}/{total_features}")
        print(f"❌ Missing Features: {missing_count}/{total_features}")
        print(f"📊 Implementation Progress: {(implemented_count/total_features)*100:.1f}%")
        
        print("\n🔍 DETAILED BREAKDOWN:")
        for feature, implemented in feature_results.items():
            status = "✅ IMPLEMENTED" if implemented else "❌ MISSING"
            print(f"   {status} {feature}")
        
        if missing_count > 0:
            print(f"\n⚠️  {missing_count} major LMS feature(s) are missing and need to be implemented.")
            print("🚧 The LMS backend has a solid foundation but requires significant additional development.")
        else:
            print("\n🎉 All major LMS features are implemented!")
        
        return missing_count == 0

if __name__ == "__main__":
    detector = MissingFeaturesDetector()
    success = detector.run_missing_features_detection()
    sys.exit(0 if success else 1)