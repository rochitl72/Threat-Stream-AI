#!/usr/bin/env python3
"""
Simple test script to verify Schema Registry connection using HTTP requests
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Get credentials
schema_registry_url = os.getenv("CONFLUENT_SCHEMA_REGISTRY_URL", "")
api_key = os.getenv("CONFLUENT_SCHEMA_REGISTRY_API_KEY") or os.getenv("CONFLUENT_API_KEY", "")
api_secret = os.getenv("CONFLUENT_SCHEMA_REGISTRY_API_SECRET") or os.getenv("CONFLUENT_API_SECRET", "")

print("=" * 60)
print("Testing Schema Registry Connection")
print("=" * 60)
print(f"Schema Registry URL: {schema_registry_url}")
print(f"API Key: {api_key[:10]}..." if api_key else "Not set")
print(f"API Secret: {'*' * 20}" if api_secret else "Not set")
print()

if not schema_registry_url:
    print("❌ Schema Registry URL not configured")
    sys.exit(1)

if not api_key or not api_secret:
    print("❌ API Key or Secret not configured")
    sys.exit(1)

# Test with requests (should be available)
try:
    import requests
    from requests.auth import HTTPBasicAuth
    
    print("Testing HTTP connection to Schema Registry...")
    
    # Test 1: Get subjects (requires authentication)
    url = f"{schema_registry_url}/subjects"
    print(f"GET {url}")
    
    response = requests.get(
        url,
        auth=HTTPBasicAuth(api_key, api_secret),
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        subjects = response.json()
        print(f"✅ SUCCESS! Schema Registry connection works!")
        print(f"✅ Found {len(subjects)} subjects")
        if subjects:
            print(f"   Subjects: {', '.join(subjects[:5])}")
            if len(subjects) > 5:
                print(f"   ... and {len(subjects) - 5} more")
        else:
            print("   (No subjects registered yet - this is normal)")
        print()
        print("=" * 60)
        print("🎉 RESULT: Your existing cluster API keys work with Schema Registry!")
        print("   You can use the same keys for both Kafka and Schema Registry.")
        print("=" * 60)
        sys.exit(0)
        
    elif response.status_code == 401:
        print(f"❌ Authentication failed (401 Unauthorized)")
        print("   The existing API keys do NOT work for Schema Registry")
        print("   You'll need to create separate Schema Registry API keys")
        print()
        print("=" * 60)
        print("❌ RESULT: Existing keys don't work. Need separate Schema Registry keys.")
        print("=" * 60)
        sys.exit(1)
        
    elif response.status_code == 404:
        print(f"⚠️  Endpoint not found (404)")
        print("   This might be a URL issue. Check the Schema Registry URL.")
        sys.exit(1)
        
    else:
        print(f"⚠️  Unexpected status code: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        sys.exit(1)
        
except ImportError:
    print("❌ 'requests' library not installed")
    print("   Install with: pip install requests")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


