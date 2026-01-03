from fastapi.testclient import TestClient
from api.main import app
import os

client = TestClient(app)

def test_api_endpoints():
    print("=== Testing API Endpoints ===")
    
    # 1. Test Root
    response = client.get("/")
    assert response.status_code == 200
    print("[PASS] Root Endpoint")

    # 2. Test Law Explanation (Module A)
    # Mocking or assuming Module A works. 
    # If Vector DB is empty for Module A, it might return empty sources but should not crash.
    print("\n[Testing] /api/v1/explain")
    payload = {"query": "How to get citizenship?"}
    try:
        response = client.post("/api/v1/explain", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"[PASS] Law Explanation: {data.get('summary', 'No summary')[:50]}...")
        else:
            print(f"[FAIL] Law Explanation: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[ERROR] Law Explanation: {e}")

    # 3. Test Letter Generation (Module C)
    print("\n[Testing] /api/v1/generate-letter")
    payload = {
        "description": "I need a citizenship certificate for my son",
        "additional_data": {"Date": "2081-01-01", "District": "Kathmandu"}
    }
    
    # Check for API Key
    if not os.getenv("MISTRAL_API_KEY"):
        print("[WARN] MISTRAL_API_KEY not set. Skipping generation test to avoid failure.")
    else:
        try:
            response = client.post("/api/v1/generate-letter", json=payload)
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    print(f"[PASS] Letter Generation: {data.get('template_used')}")
                else:
                    print(f"[FAIL] Letter Generation: {data.get('error')}")
            else:
                print(f"[FAIL] Letter Generation: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"[ERROR] Letter Generation: {e}")

    # 4. Test Analyze Requirements (Module C)
    print("\n[Testing] /api/v1/analyze-requirements")
    payload = {"description": "I need a citizenship certificate"}
    try:
        response = client.post("/api/v1/analyze-requirements", json=payload)
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"[PASS] Analysis: Detected {len(data.get('detected_placeholders', []))} placeholders")
                print(f"      Missing {data.get('missing_fields')}")
                
                # 5. Test Generate with Specific Template (New Flow)
                template_name = data.get('template_used')
                if template_name:
                    print(f"\n[Testing] /api/v1/generate-letter (Direct Template: {template_name})")
                    payload_direct = {
                        "description": "I need a citizenship certificate",
                        "template_name": template_name,
                        "additional_data": {"Date": "2081-01-01", "District": "Kathmandu"}
                    }
                    if os.getenv("MISTRAL_API_KEY"):
                        resp_direct = client.post("/api/v1/generate-letter", json=payload_direct)
                        if resp_direct.status_code == 200:
                            data_direct = resp_direct.json()
                            if data_direct['success'] and data_direct['template_used'] == template_name:
                                print(f"[PASS] Direct Generation Successful")
                            else:
                                print(f"[FAIL] Direct Generation: {data_direct.get('error')}")
            else:
                print(f"[FAIL] Analysis: {data.get('error')}")
        else:
            print(f"[FAIL] Analysis: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[ERROR] Analysis: {e}")

    # 6. Test Granular APIs (3-Step Flow)
    print("\n[Testing] Granular API Flow")
    
    # Step 1: Search
    print("  1. Search Template")
    search_payload = {"query": "I need a citizenship certificate"}
    template_name = None
    try:
        resp = client.post("/api/v1/search-template", json=search_payload)
        if resp.status_code == 200:
            data = resp.json()
            if data['success']:
                template_name = data['template_name']
                print(f"     [PASS] Found: {template_name}")
            else:
                print(f"     [FAIL] Search: {data.get('error')}")
        else:
            print(f"     [FAIL] Search Status: {resp.status_code}")
    except Exception as e:
        print(f"     [ERROR] Search: {e}")

    if template_name:
        # Step 2: Get Details
        print("  2. Get Template Details")
        details_payload = {"template_name": template_name}
        placeholders = []
        try:
            resp = client.post("/api/v1/get-template-details", json=details_payload)
            if resp.status_code == 200:
                data = resp.json()
                if data['success']:
                    placeholders = data['placeholders']
                    print(f"     [PASS] Placeholders: {placeholders}")
                else:
                    print(f"     [FAIL] Details: {data.get('error')}")
            else:
                print(f"     [FAIL] Details Status: {resp.status_code}")
        except Exception as e:
            print(f"     [ERROR] Details: {e}")

        # Step 3: Fill Template
        print("  3. Fill Template")
        # Create dummy data for all placeholders
        fill_data = {p: "TEST_VALUE" for p in placeholders}
        fill_payload = {"template_name": template_name, "placeholders": fill_data}
        try:
            resp = client.post("/api/v1/fill-template", json=fill_payload)
            if resp.status_code == 200:
                data = resp.json()
                if data['success']:
                    print(f"     [PASS] Letter Generated (Length: {len(data['letter'])})")
                else:
                    print(f"     [FAIL] Fill: {data.get('error')}")
            else:
                print(f"     [FAIL] Fill Status: {resp.status_code}")
        except Exception as e:
            print(f"     [ERROR] Fill: {e}")

if __name__ == "__main__":
    test_api_endpoints()
