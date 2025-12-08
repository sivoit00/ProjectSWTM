import requests
import sys

BASE_URL = "http://localhost:8000"

def test_without_auth():
    print("Testing endpoints WITHOUT authentication...")
    
    endpoints = [
        "/kunden",
        "/auftraege",
        "/fahrzeuge"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 401:
                print(f"✅ {endpoint}: Correctly blocked (401)")
            else:
                print(f"❌ {endpoint}: Should be blocked but got {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")

def test_with_invalid_token():
    print("\nTesting endpoints WITH invalid token...")
    
    headers = {"Authorization": "Bearer invalid_token_123"}
    
    endpoints = [
        "/kunden",
        "/auftraege",
        "/fahrzeuge"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            if response.status_code == 401:
                print(f"✅ {endpoint}: Correctly blocked (401)")
            else:
                print(f"❌ {endpoint}: Should be blocked but got {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")

def test_chat_without_auth():
    print("\nTesting chat WITHOUT authentication (should work)...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/ki-orchestrator/message",
            json={"message": "Hallo"}
        )
        if response.status_code == 200:
            print(f"✅ Chat: Works without auth (200)")
        else:
            print(f"❌ Chat: Got {response.status_code}")
    except Exception as e:
        print(f"❌ Chat: Error - {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("AUTH SECURITY TEST")
    print("=" * 50)
    
    test_without_auth()
    test_with_invalid_token()
    test_chat_without_auth()
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("=" * 50)
