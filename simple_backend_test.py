#!/usr/bin/env python3
"""
Simple Backend API Testing Suite for Supabase Connection
Tests basic connectivity and existing functionality
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

# Get backend URL from supervisor configuration
BACKEND_URL = "https://auth-creds-update.preview.emergentagent.com/api"

class SimpleAPITester:
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
                self.log_test("Health Check", True, f"Backend is healthy: {data.get('service', 'Unknown service')}")
                return True
            else:
                self.log_test("Health Check", False, f"Unexpected response: {data}")
                return False
        else:
            self.log_test("Health Check", False, f"Status code: {response.status_code}")
            return False
    
    def test_supabase_connection(self):
        """Test Supabase database connection by checking if we can query users"""
        print("🔍 Testing Supabase Database Connection...")
        
        # We'll test this by trying to access a protected endpoint without auth
        # This should fail with 403, not 500 (which would indicate DB connection issues)
        success, response, error = self.make_request("GET", "/users")
        
        if not success:
            self.log_test("Supabase Connection", False, f"Request failed: {error}")
            return False
            
        if response.status_code == 403:
            self.log_test("Supabase Connection", True, "Database connection working (got expected 403 for unauthorized access)")
            return True
        elif response.status_code == 500:
            self.log_test("Supabase Connection", False, "Database connection failed (500 error)")
            return False
        else:
            self.log_test("Supabase Connection", True, f"Unexpected but non-error response: {response.status_code}")
            return True
    
    def test_database_query(self):
        """Test direct database access using Python client"""
        print("🔍 Testing Direct Database Query...")
        
        try:
            import os
            from dotenv import load_dotenv
            from supabase import create_client
            
            # Load environment variables
            load_dotenv('/app/backend/.env')
            url = os.environ.get('SUPABASE_URL')
            key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
            
            if not url or not key:
                self.log_test("Database Query", False, "Missing Supabase credentials")
                return False
            
            # Create Supabase client
            supabase = create_client(url, key)
            
            # Try to query users table
            result = supabase.table("users").select("id, username, role").execute()
            
            if result.data is not None:
                user_count = len(result.data)
                self.log_test("Database Query", True, f"Successfully queried users table. Found {user_count} users.")
                
                # Show sample data
                if result.data:
                    print("   Sample users:")
                    for user in result.data[:3]:  # Show first 3 users
                        print(f"     - {user.get('username', 'N/A')} ({user.get('role', 'N/A')})")
                
                return True
            else:
                self.log_test("Database Query", False, "Query returned None")
                return False
                
        except Exception as e:
            self.log_test("Database Query", False, f"Error: {str(e)}")
            return False
    
    def test_courses_table(self):
        """Test courses table access"""
        print("🔍 Testing Courses Table Access...")
        
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
            
            # Try to query courses table
            result = supabase.table("courses").select("id, title, approval_status").execute()
            
            if result.data is not None:
                course_count = len(result.data)
                self.log_test("Courses Table", True, f"Successfully queried courses table. Found {course_count} courses.")
                
                # Show sample data
                if result.data:
                    print("   Sample courses:")
                    for course in result.data[:3]:  # Show first 3 courses
                        print(f"     - {course.get('title', 'N/A')} ({course.get('approval_status', 'N/A')})")
                
                return True
            else:
                self.log_test("Courses Table", False, "Query returned None")
                return False
                
        except Exception as e:
            self.log_test("Courses Table", False, f"Error: {str(e)}")
            return False
    
    def test_all_tables(self):
        """Test access to all expected tables"""
        print("🔍 Testing All Database Tables...")
        
        tables = [
            "users", "courses", "enrollments", "attendance", "tasks", 
            "task_submissions", "mock_interviews", "reports", 
            "fee_reminders", "materials", "certificates"
        ]
        
        results = []
        
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
            
            for table in tables:
                try:
                    result = supabase.table(table).select("*").limit(1).execute()
                    if result.data is not None:
                        count_result = supabase.table(table).select("*", count="exact").execute()
                        count = count_result.count if count_result.count is not None else len(result.data)
                        print(f"   ✅ {table}: {count} records")
                        results.append(True)
                    else:
                        print(f"   ❌ {table}: Query failed")
                        results.append(False)
                except Exception as e:
                    print(f"   ❌ {table}: Error - {str(e)}")
                    results.append(False)
            
            success_count = sum(results)
            total_count = len(results)
            
            if success_count == total_count:
                self.log_test("All Tables", True, f"All {total_count} tables accessible")
                return True
            else:
                self.log_test("All Tables", False, f"Only {success_count}/{total_count} tables accessible")
                return False
                
        except Exception as e:
            self.log_test("All Tables", False, f"Setup error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("=" * 60)
        print("🚀 Simple LMS Backend API Testing Suite")
        print("=" * 60)
        
        results = []
        
        # Test 1: Health Check
        results.append(self.test_health_check())
        
        # Test 2: Supabase Connection
        results.append(self.test_supabase_connection())
        
        # Test 3: Database Query
        results.append(self.test_database_query())
        
        # Test 4: Courses Table
        results.append(self.test_courses_table())
        
        # Test 5: All Tables
        results.append(self.test_all_tables())
        
        # Summary
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(results)
        total = len(results)
        
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        if passed == total:
            print("\n🎉 All tests passed! Supabase connection is working correctly.")
        else:
            print(f"\n⚠️  {total - passed} test(s) failed. Please check the issues above.")
        
        return results

if __name__ == "__main__":
    tester = SimpleAPITester()
    results = tester.run_all_tests()
    
    # Exit with error code if any tests failed
    if not all(results):
        sys.exit(1)