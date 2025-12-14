#!/bin/bash
# Final script to create Schema Registry API key

cd "$(dirname "$0")/.."

echo "=========================================="
echo "Create Schema Registry API Key"
echo "=========================================="
echo

# Method 1: Try CLI (requires interactive login)
echo "Method 1: Using Confluent CLI"
echo "------------------------------"
echo
echo "This will open a browser for authentication."
echo "Please follow the prompts."
echo
read -p "Press Enter to start login, or Ctrl+C to skip..."

./bin/confluent login

if [ $? -eq 0 ]; then
    echo
    echo "✅ Login successful!"
    echo
    echo "Creating Schema Registry API key..."
    echo
    
    OUTPUT=$(./bin/confluent api-key create \
      --resource lsrc-rnd6q0 \
      --description "ThreatStream AI Schema Registry" \
      --output json 2>&1)
    
    if [ $? -eq 0 ]; then
        echo "$OUTPUT"
        echo
        echo "=========================================="
        echo "✅ API Key Created Successfully!"
        echo "=========================================="
        echo
        echo "Please copy the 'key' and 'secret' from above."
        echo "Then update your .env file."
        exit 0
    else
        echo "❌ Failed to create API key:"
        echo "$OUTPUT"
    fi
else
    echo "❌ Login failed"
fi

echo
echo "=========================================="
echo "Alternative: Use Confluent Cloud UI"
echo "=========================================="
echo
echo "If CLI doesn't work, use the web interface:"
echo "1. Go to: https://confluent.cloud"
echo "2. Navigate to: Stream Governance → Schema Registry"
echo "3. Click 'Endpoints' tab"
echo "4. Look for 'API Keys' section"
echo "5. Create new API key for Schema Registry (lsrc-rnd6q0)"
echo

