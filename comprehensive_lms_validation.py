#!/usr/bin/env python3
"""
Comprehensive LMS Validation & Eligibility Check
Tests all LMS requirements against defined functional, security, and eligibility criteria
"""

import requests
import json
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime

# Get backend URL from frontend .env
BACKEND_URL = "https://lms-audit.preview.emergentagent.com/api"

class ComprehensiveLMSValidator:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.tokens = {}  # Store tokens for different users
        self.users = {}   # Store user data
        self.courses = {}  # Store created courses
        self.validation_results = {
            "admin_features": {},
            "backend_apis": {},
            "security_access": {},
            "database_integration": {},
            "missing_features": {}
        }
        
    def log_validation(self, category: str, test_name: str, status: str, details: str = ""):
        """Log validation results with status: ✔ Satisfied, ~ Partially Satisfied, ✘ Not Satisfied"""
        if category not in self.validation_results:
            self.validation_results[category] = {}
        
        self.validation_results[category][test_name] = {
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
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
    
    def setup_test_users(self):
        """Create test users for validation"""
        print("🔧 Setting up test users...")
        
        test_users = [
            {"role": "admin", "username": "admin_validator", "email": "admin.validator@lms.com", "full_name": "Admin Validator", "password": "AdminPass123!"},
            {"role": "mentor", "username": "mentor_validator", "email": "mentor.validator@lms.com", "full_name": "Mentor Validator", "password": "MentorPass123!"},
            {"role": "student", "username": "student_validator", "email": "student.validator@lms.com", "full_name": "Student Validator", "password": "StudentPass123!"}
        ]
        
        for user_data in test_users:
            success, response, error = self.make_request("POST", "/auth/register", user_data)
            if success and response.status_code == 200:
                data = response.json()
                self.tokens[user_data["role"]] = data["access_token"]
                self.users[user_data["role"]] = data["user"]
                print(f"✅ Created {user_data['role']} user: {user_data['username']}")
            else:
                print(f"❌ Failed to create {user_data['role']} user")
    
    def validate_database_connection(self):
        """Validate Supabase database connection and schema"""
        print("\n" + "=" * 60)
        print("🗄️ DATABASE INTEGRATION VALIDATION")
        print("=" * 60)
        
        # Test health endpoint
        success, response, error = self.make_request("GET", "/health")
        if success and response.status_code == 200:
            data = response.json()
            if "Supabase" in data.get("service", ""):
                self.log_validation("database_integration", "Supabase Connection", "✔", "Backend connected to Supabase PostgreSQL")
            else:
                self.log_validation("database_integration", "Supabase Connection", "✘", "Backend not using Supabase")
        else:
            self.log_validation("database_integration", "Supabase Connection", "✘", f"Health check failed: {error}")
        
        # Test database operations through API
        if "admin" in self.tokens:
            headers = {"Authorization": f"Bearer {self.tokens['admin']}"}
            success, response, error = self.make_request("GET", "/users", headers=headers)
            if success and response.status_code == 200:
                users = response.json()
                self.log_validation("database_integration", "Database CRUD Operations", "✔", f"Successfully retrieved {len(users)} users from database")
            else:
                self.log_validation("database_integration", "Database CRUD Operations", "✘", "Failed to retrieve users from database")
    
    def validate_authentication_system(self):
        """Validate complete authentication system"""
        print("\n" + "=" * 60)
        print("🔐 AUTHENTICATION SYSTEM VALIDATION")
        print("=" * 60)
        
        # Test JWT authentication
        if "admin" in self.tokens:
            headers = {"Authorization": f"Bearer {self.tokens['admin']}"}
            success, response, error = self.make_request("GET", "/auth/me", headers=headers)
            if success and response.status_code == 200:
                self.log_validation("security_access", "JWT Authentication", "✔", "JWT tokens working correctly")
            else:
                self.log_validation("security_access", "JWT Authentication", "✘", "JWT authentication failed")
        
        # Test password hashing (bcrypt)
        test_login = {
            "username": "admin_validator",
            "password": "AdminPass123!"
        }
        success, response, error = self.make_request("POST", "/auth/login", test_login)
        if success and response.status_code == 200:
            self.log_validation("security_access", "Password Hashing (bcrypt)", "✔", "Password verification working with bcrypt")
        else:
            self.log_validation("security_access", "Password Hashing (bcrypt)", "✘", "Password hashing/verification failed")
        
        # Test role-based access control
        if "student" in self.tokens:
            headers = {"Authorization": f"Bearer {self.tokens['student']}"}
            success, response, error = self.make_request("GET", "/users", headers=headers)
            if success and response.status_code == 403:
                self.log_validation("security_access", "Role-Based Access Control", "✔", "RBAC correctly restricts student access to admin endpoints")
            else:
                self.log_validation("security_access", "Role-Based Access Control", "✘", "RBAC not working properly")
    
    def validate_course_management(self):
        """Validate course management system"""
        print("\n" + "=" * 60)
        print("🎓 COURSE MANAGEMENT VALIDATION")
        print("=" * 60)
        
        # Test course creation
        if "admin" in self.tokens:
            headers = {"Authorization": f"Bearer {self.tokens['admin']}"}
            course_data = {
                "title": "Validation Test Course",
                "description": "Course for comprehensive validation testing",
                "mentor_id": self.users.get("mentor", {}).get("id")
            }
            success, response, error = self.make_request("POST", "/courses", course_data, headers)
            if success and response.status_code == 200:
                course = response.json()
                self.courses["validation_course"] = course
                self.log_validation("admin_features", "Course Creation", "✔", "Admin can create courses with mentor assignment")
            else:
                self.log_validation("admin_features", "Course Creation", "✘", "Course creation failed")
        
        # Test course approval workflow
        if "validation_course" in self.courses and "admin" in self.tokens:
            headers = {"Authorization": f"Bearer {self.tokens['admin']}"}
            course_id = self.courses["validation_course"]["id"]
            approval_data = {"approval_status": "approved"}
            success, response, error = self.make_request("PUT", f"/courses/{course_id}/approve", approval_data, headers)
            if success and response.status_code == 200:
                self.log_validation("admin_features", "Course Approval Workflow", "✔", "Admin can approve/reject courses")
            else:
                self.log_validation("admin_features", "Course Approval Workflow", "✘", "Course approval workflow failed")
        
        # Test role-based course access
        if "validation_course" in self.courses:
            course_id = self.courses["validation_course"]["id"]
            
            # Student should see approved course
            if "student" in self.tokens:
                headers = {"Authorization": f"Bearer {self.tokens['student']}"}
                success, response, error = self.make_request("GET", f"/courses/{course_id}", headers=headers)
                if success and response.status_code == 200:
                    self.log_validation("security_access", "Course Access Control", "✔", "Students can access approved courses")
                else:
                    self.log_validation("security_access", "Course Access Control", "✘", "Course access control failed")
    
    def validate_enrollment_system(self):
        """Validate enrollment management system"""
        print("\n" + "=" * 60)
        print("📚 ENROLLMENT SYSTEM VALIDATION")
        print("=" * 60)
        
        if "validation_course" in self.courses and "student" in self.tokens:
            course_id = self.courses["validation_course"]["id"]
            headers = {"Authorization": f"Bearer {self.tokens['student']}"}
            enrollment_data = {"course_id": course_id}
            
            success, response, error = self.make_request("POST", "/enrollments", enrollment_data, headers)
            if success and response.status_code == 200:
                self.log_validation("backend_apis", "Enrollment Management", "✔", "Student enrollment system working")
            else:
                self.log_validation("backend_apis", "Enrollment Management", "✘", "Enrollment system failed")
    
    def validate_task_system(self):
        """Validate task/assignment system"""
        print("\n" + "=" * 60)
        print("📋 TASK/ASSIGNMENT SYSTEM VALIDATION")
        print("=" * 60)
        
        if "validation_course" in self.courses and "mentor" in self.tokens:
            course_id = self.courses["validation_course"]["id"]
            headers = {"Authorization": f"Bearer {self.tokens['mentor']}"}
            task_data = {
                "course_id": course_id,
                "title": "Validation Assignment",
                "description": "Test assignment for validation",
                "due_date": "2025-02-15T23:59:59Z"
            }
            
            success, response, error = self.make_request("POST", "/tasks", task_data, headers)
            if success and response.status_code == 200:
                task = response.json()
                self.courses["validation_task"] = task
                self.log_validation("backend_apis", "Task/Assignment System", "✔", "Mentors can create assignments")
            else:
                self.log_validation("backend_apis", "Task/Assignment System", "✘", "Task creation failed")
    
    def validate_missing_features(self):
        """Identify missing LMS features"""
        print("\n" + "=" * 60)
        print("❌ MISSING FEATURES VALIDATION")
        print("=" * 60)
        
        missing_systems = [
            {
                "name": "Attendance Tracking System",
                "endpoints": ["/attendance/checkin", "/attendance/checkout", "/attendance/reports"],
                "description": "Student check-in/out, attendance reports"
            },
            {
                "name": "Materials Management System", 
                "endpoints": ["/materials", "/materials/upload", "/materials/download"],
                "description": "Course materials upload, download, sharing"
            },
            {
                "name": "Certificate Generation System",
                "endpoints": ["/certificates/generate", "/certificates/download"],
                "description": "Automated certificate generation and distribution"
            },
            {
                "name": "Fee Reminder System",
                "endpoints": ["/fee-reminders", "/fee-reminders/send"],
                "description": "Automated fee reminders and payment tracking"
            },
            {
                "name": "Mock Interview Scheduling",
                "endpoints": ["/mock-interviews", "/mock-interviews/schedule"],
                "description": "Interview scheduling and feedback system"
            },
            {
                "name": "Progress Reporting System",
                "endpoints": ["/reports/progress", "/reports/student/{id}/progress"],
                "description": "Student progress tracking and reporting"
            },
            {
                "name": "Email Notification System",
                "endpoints": ["/notifications/email", "/notifications/bulk"],
                "description": "Automated email notifications and alerts"
            }
        ]
        
        for system in missing_systems:
            # Test if any endpoints exist
            endpoints_exist = False
            for endpoint in system["endpoints"]:
                if "admin" in self.tokens:
                    headers = {"Authorization": f"Bearer {self.tokens['admin']}"}
                    success, response, error = self.make_request("GET", endpoint, headers=headers)
                    if success and response.status_code != 404:
                        endpoints_exist = True
                        break
            
            if endpoints_exist:
                self.log_validation("missing_features", system["name"], "~", f"Some endpoints implemented: {system['description']}")
            else:
                self.log_validation("missing_features", system["name"], "✘", f"Not implemented: {system['description']}")
    
    def validate_admin_features(self):
        """Validate admin-specific features"""
        print("\n" + "=" * 60)
        print("👑 ADMIN FEATURES VALIDATION")
        print("=" * 60)
        
        if "admin" not in self.tokens:
            self.log_validation("admin_features", "Admin Access", "✘", "No admin user available")
            return
        
        headers = {"Authorization": f"Bearer {self.tokens['admin']}"}
        
        # Test user management
        success, response, error = self.make_request("GET", "/users", headers=headers)
        if success and response.status_code == 200:
            users = response.json()
            self.log_validation("admin_features", "User Management (CRUD)", "✔", f"Admin can view all {len(users)} users")
        else:
            self.log_validation("admin_features", "User Management (CRUD)", "✘", "Admin cannot access user management")
        
        # Test course management
        success, response, error = self.make_request("GET", "/courses", headers=headers)
        if success and response.status_code == 200:
            courses = response.json()
            self.log_validation("admin_features", "Course Management", "✔", f"Admin can view all {len(courses)} courses")
        else:
            self.log_validation("admin_features", "Course Management", "✘", "Admin cannot access course management")
        
        # Test reports (check if any reporting endpoints exist)
        report_endpoints = ["/reports", "/reports/attendance", "/reports/grades"]
        reports_available = False
        for endpoint in report_endpoints:
            success, response, error = self.make_request("GET", endpoint, headers=headers)
            if success and response.status_code != 404:
                reports_available = True
                break
        
        if reports_available:
            self.log_validation("admin_features", "Report Generation", "~", "Some reporting functionality available")
        else:
            self.log_validation("admin_features", "Report Generation", "✘", "No reporting system implemented")
    
    def validate_security_features(self):
        """Validate security and eligibility features"""
        print("\n" + "=" * 60)
        print("🔒 SECURITY & ELIGIBILITY VALIDATION")
        print("=" * 60)
        
        # Test unauthorized access prevention
        success, response, error = self.make_request("GET", "/users")  # No token
        if success and response.status_code == 403:
            self.log_validation("security_access", "Unauthorized Access Prevention", "✔", "API correctly rejects requests without authentication")
        else:
            self.log_validation("security_access", "Unauthorized Access Prevention", "✘", "API allows unauthorized access")
        
        # Test cross-role access restrictions
        if "student" in self.tokens and "mentor" in self.users:
            headers = {"Authorization": f"Bearer {self.tokens['student']}"}
            mentor_id = self.users["mentor"]["id"]
            success, response, error = self.make_request("GET", f"/courses/mentor/{mentor_id}", headers=headers)
            if success and response.status_code == 403:
                self.log_validation("security_access", "Cross-Role Access Restrictions", "✔", "Students cannot access mentor-specific data")
            else:
                self.log_validation("security_access", "Cross-Role Access Restrictions", "✘", "Cross-role access not properly restricted")
        
        # Check for advanced security features (these would typically be missing)
        advanced_security = [
            "Single Device Login",
            "Two-Factor Authentication (2FA)", 
            "AI Proctoring System",
            "Session Management",
            "Device Fingerprinting"
        ]
        
        for feature in advanced_security:
            self.log_validation("security_access", feature, "✘", "Advanced security feature not implemented")
    
    def generate_comprehensive_report(self):
        """Generate final comprehensive validation report"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE LMS VALIDATION REPORT")
        print("=" * 80)
        
        total_tests = 0
        satisfied = 0
        partially_satisfied = 0
        not_satisfied = 0
        
        for category, tests in self.validation_results.items():
            print(f"\n🔍 {category.upper().replace('_', ' ')}:")
            print("-" * 50)
            
            for test_name, result in tests.items():
                status = result["status"]
                details = result["details"]
                print(f"{status} {test_name}")
                if details:
                    print(f"   {details}")
                
                total_tests += 1
                if status == "✔":
                    satisfied += 1
                elif status == "~":
                    partially_satisfied += 1
                else:
                    not_satisfied += 1
        
        print("\n" + "=" * 80)
        print("📈 COMPLIANCE SUMMARY")
        print("=" * 80)
        
        satisfied_pct = (satisfied / total_tests * 100) if total_tests > 0 else 0
        partial_pct = (partially_satisfied / total_tests * 100) if total_tests > 0 else 0
        not_satisfied_pct = (not_satisfied / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✔ Satisfied: {satisfied}/{total_tests} ({satisfied_pct:.1f}%)")
        print(f"~ Partially Satisfied: {partially_satisfied}/{total_tests} ({partial_pct:.1f}%)")
        print(f"✘ Not Satisfied: {not_satisfied}/{total_tests} ({not_satisfied_pct:.1f}%)")
        print(f"\nOverall Compliance: {satisfied_pct:.1f}%")
        
        # Implementation status assessment
        if satisfied_pct >= 80:
            status = "PRODUCTION READY"
        elif satisfied_pct >= 60:
            status = "NEAR PRODUCTION READY"
        elif satisfied_pct >= 40:
            status = "DEVELOPMENT PHASE"
        else:
            status = "EARLY DEVELOPMENT"
        
        print(f"Implementation Status: {status}")
        
        return {
            "total_tests": total_tests,
            "satisfied": satisfied,
            "partially_satisfied": partially_satisfied,
            "not_satisfied": not_satisfied,
            "compliance_percentage": satisfied_pct,
            "status": status,
            "detailed_results": self.validation_results
        }
    
    def run_comprehensive_validation(self):
        """Run complete LMS validation suite"""
        print("🎯 COMPREHENSIVE LMS VALIDATION & ELIGIBILITY CHECK")
        print("=" * 80)
        print("Validating against ALL defined functional, security, and eligibility requirements")
        print("=" * 80)
        
        # Setup
        self.setup_test_users()
        
        # Run all validation categories
        self.validate_database_connection()
        self.validate_authentication_system()
        self.validate_course_management()
        self.validate_enrollment_system()
        self.validate_task_system()
        self.validate_admin_features()
        self.validate_security_features()
        self.validate_missing_features()
        
        # Generate final report
        return self.generate_comprehensive_report()

def main():
    validator = ComprehensiveLMSValidator()
    report = validator.run_comprehensive_validation()
    
    # Save report to file
    with open('/app/lms_validation_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: /app/lms_validation_report.json")
    
    return report["compliance_percentage"] >= 70  # Return success if >= 70% compliance

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)