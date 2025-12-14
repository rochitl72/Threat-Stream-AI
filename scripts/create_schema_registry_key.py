#!/usr/bin/env python3
"""
Create Schema Registry API key using Confluent Cloud REST API
"""

import requests
import json
import sys
from pathlib import Path
from dotenv import load_dotenv
import os

# Load .env
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

print("=" * 60)
print("Create Schema Registry API Key")
print("=" * 60)
print()

# Schema Registry details
SCHEMA_REGISTRY_ID = "lsrc-rnd6q0"
ENVIRONMENT_ID = "env-n0grr6"

print("To create a Schema Registry API key, you need to:")
print("1. Get your Confluent Cloud API token")
print("2. Use it to create the Schema Registry API key")
print()
print("Option 1: Use Confluent Cloud UI (Easier)")
print("- Go to: https://confluent.cloud")
print("- Navigate to: Stream Governance → Schema Registry")
print("- Look for 'API Keys' or 'Endpoints' tab")
print("- Create a new API key for Schema Registry")
print()
print("Option 2: Use Confluent CLI")
print("Run these commands:")
print()
print("  # Install CLI")
print("  curl -sL --http1.1 https://cnfl.io/cli | sh -s -- latest")
print()
print("  # Add to PATH")
print("  export PATH=$PATH:$HOME/bin")
print()
print("  # Login")
print("  confluent login")
print()
print("  # Create Schema Registry API key")
print(f"  confluent api-key create --resource {SCHEMA_REGISTRY_ID} --description 'ThreatStream AI Schema Registry'")
print()
print("Option 3: Manual REST API (Advanced)")
print("You'll need:")
print("- Confluent Cloud API token (from Account Settings → API Tokens)")
print("- Then use the REST API to create the key")
print()

# Check if we can use existing credentials to get a token
print("=" * 60)
print("Quick Check: Do you have Confluent Cloud API token?")
print("=" * 60)
print()
print("If you have an API token, you can create the key programmatically.")
print("Otherwise, the easiest way is through the UI or CLI.")
print()

# Provide instructions for UI method
print("\n" + "=" * 60)
print("RECOMMENDED: Create via UI")
print("=" * 60)
print()
print("Steps:")
print("1. Go to: https://confluent.cloud/environments/env-n0grr6/stream-governance/schema-registry")
print("2. Click on 'Endpoints' tab")
print("3. Look for 'API Keys' section or button")
print("4. Click 'Create API Key' or 'Add Key'")
print("5. Select resource: Schema Registry (lsrc-rnd6q0)")
print("6. Save the API key and secret")
print()
print("If you can't find it in the UI, the Schema Registry might not")
print("support separate API keys in the Essentials package.")
print("In that case, you might need to use the cluster API keys")
print("with different authentication method.")
print()

sys.exit(0)


