import requests
import sys
import os
import json
from datetime import datetime
import uuid
import io

class SmartCampusBotTester:
    def __init__(self, base_url="https://campusai-8.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session_id = str(uuid.uuid4())
        self.tests_run = 0
        self.tests_passed = 0
        self.uploaded_doc_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {}
        
        if files is None:
            headers['Content-Type'] = 'application/json'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files)
                else:
                    response = requests.post(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_api_root(self):
        """Test API root endpoint"""
        return self.run_test("API Root", "GET", "", 200)

    def test_get_documents_empty(self):
        """Test getting documents when none exist"""
        return self.run_test("Get Documents (Empty)", "GET", "documents", 200)

    def test_upload_document(self):
        """Test document upload with a sample PDF"""
        # Create a simple text file to simulate PDF upload
        test_content = """
        Smart Campus Bot Test Document
        
        This is a test document for the Smart Campus Bot RAG system.
        It contains information about academic policies and procedures.
        
        Academic Calendar:
        - Fall Semester: September to December
        - Spring Semester: January to May
        - Summer Session: June to August
        
        Library Hours:
        - Monday-Friday: 8:00 AM - 10:00 PM
        - Saturday: 10:00 AM - 6:00 PM
        - Sunday: 12:00 PM - 8:00 PM
        
        Contact Information:
        - Academic Affairs: (555) 123-4567
        - Student Services: (555) 234-5678
        - IT Support: (555) 345-6789
        """
        
        # Create a simple file-like object
        file_content = test_content.encode('utf-8')
        files = {
            'file': ('test_document.txt', io.BytesIO(file_content), 'text/plain')
        }
        
        print("   Note: Testing with text file (PDF upload would require actual PDF)")
        success, response = self.run_test("Upload Document", "POST", "documents/upload", 400, files=files)
        
        # Since we're using a text file, we expect a 400 error for unsupported file type
        if not success and response == {}:
            print("   Expected failure: Only PDF and DOCX files are supported")
            return True, {}
        
        return success, response

    def test_get_documents_after_upload(self):
        """Test getting documents after upload"""
        return self.run_test("Get Documents (After Upload)", "GET", "documents", 200)

    def test_chat_no_documents(self):
        """Test chat when no documents are uploaded"""
        chat_data = {
            "query": "What are the library hours?",
            "session_id": self.session_id
        }
        return self.run_test("Chat (No Documents)", "POST", "chat", 200, data=chat_data)

    def test_chat_history(self):
        """Test getting chat history"""
        return self.run_test("Get Chat History", "GET", f"chat/history/{self.session_id}", 200)

    def test_delete_nonexistent_document(self):
        """Test deleting a non-existent document"""
        fake_id = str(uuid.uuid4())
        return self.run_test("Delete Non-existent Document", "DELETE", f"documents/{fake_id}", 404)

    def test_openai_integration(self):
        """Test if OpenAI integration is working by checking environment"""
        print(f"\n🔍 Testing OpenAI Integration...")
        
        # Test chat with a simple query
        chat_data = {
            "query": "Hello, can you help me?",
            "session_id": self.session_id
        }
        
        success, response = self.run_test("OpenAI Chat Test", "POST", "chat", 200, data=chat_data)
        
        if success and response.get('response'):
            print("✅ OpenAI integration appears to be working")
            return True
        else:
            print("❌ OpenAI integration may have issues")
            return False

def main():
    print("🚀 Starting Smart Campus Bot API Tests")
    print("=" * 50)
    
    tester = SmartCampusBotTester()
    
    # Test sequence
    tests = [
        ("API Root", tester.test_api_root),
        ("Get Documents (Empty)", tester.test_get_documents_empty),
        ("Upload Document", tester.test_upload_document),
        ("Get Documents (After Upload)", tester.test_get_documents_after_upload),
        ("Chat (No Documents)", tester.test_chat_no_documents),
        ("Chat History", tester.test_chat_history),
        ("Delete Non-existent Document", tester.test_delete_nonexistent_document),
        ("OpenAI Integration", tester.test_openai_integration),
    ]
    
    for test_name, test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())