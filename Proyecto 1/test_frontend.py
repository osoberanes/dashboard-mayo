#!/usr/bin/env python3
import requests
import sys
import time

def test_frontend():
    """Test que el frontend responda correctamente"""
    try:
        print("Testing frontend access...")
        response = requests.get("http://localhost:8000/", timeout=5)
        
        if response.status_code == 200:
            if "Sistema de Análisis" in response.text:
                print("SUCCESS: Frontend is serving HTML correctly")
                return True
            else:
                print(f"WARNING: Frontend responded but content unexpected: {response.text[:200]}...")
                return False
        else:
            print(f"ERROR: Frontend returned status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to server. Is it running on localhost:8000?")
        return False
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        return False

def test_api():
    """Test que la API responda correctamente"""
    try:
        print("Testing API access...")
        response = requests.get("http://localhost:8000/api", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if "message" in data:
                print("SUCCESS: API is responding correctly")
                return True
            else:
                print("WARNING: API responded but format unexpected")
                return False
        else:
            print(f"ERROR: API returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"ERROR: API test failed: {e}")
        return False

def test_static_files():
    """Test que los archivos estáticos se sirvan"""
    try:
        print("Testing static files...")
        response = requests.get("http://localhost:8000/static/css/styles.css", timeout=5)
        
        if response.status_code == 200:
            print("SUCCESS: Static files are being served")
            return True
        else:
            print(f"WARNING: Static files returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"ERROR: Static files test failed: {e}")
        return False

def main():
    print("Testing Sistema de Análisis de Producción")
    print("=" * 45)
    
    # Give server a moment to start if just launched
    time.sleep(2)
    
    tests = [
        ("Frontend HTML", test_frontend),
        ("API Endpoint", test_api),
        ("Static Files", test_static_files),
    ]
    
    passed = 0
    for name, test_func in tests:
        print(f"\n[{name}]:")
        if test_func():
            passed += 1
        print("-" * 30)
    
    print(f"\nResult: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("\nSUCCESS: All tests passed!")
        print("You can access the system at: http://localhost:8000")
    elif passed > 0:
        print("\nPARTIAL: Some components are working")
        print("Check the errors above for details")
    else:
        print("\nFAILED: System is not responding correctly")
        print("Make sure the server is running: py run.py")
    
    return passed == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)