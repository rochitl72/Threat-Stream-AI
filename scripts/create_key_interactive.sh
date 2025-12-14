#!/bin/bash
# Interactive script to create Schema Registry API key

cd "$(dirname "$0")/.."

echo "=========================================="
echo "Create Schema Registry API Key"
echo "=========================================="
echo

# Check if CLI exists
if [ ! -f "./bin/confluent" ]; then
    echo "❌ Confluent CLI not found in ./bin/"
    echo "   Run: curl -sL --http1.1 https://cnfl.io/cli | sh -s -- latest"
    exit 1
fi

echo "✅ Confluent CLI found"
echo

# Check if logged in
echo "Checking login status..."
if ! ./bin/confluent current &> /dev/null; then
    echo "⚠️  Not logged in. Please login:"
    echo
    echo "   ./bin/confluent login"
    echo
    echo "This will open a browser for authentication."
    echo
    read -p "Press Enter after you've logged in, or Ctrl+C to cancel..."
fi

echo
echo "Creating Schema Registry API key..."
echo "Resource: lsrc-rnd6q0"
echo

./bin/confluent api-key create \
  --resource lsrc-rnd6q0 \
  --description "ThreatStream AI Schema Registry" \
  --output json

echo
echo "=========================================="
echo "✅ Done!"
echo "=========================================="
echo
echo "Copy the 'key' and 'secret' from above and update your .env file:"
echo "  CONFLUENT_SCHEMA_REGISTRY_API_KEY=<key>"
echo "  CONFLUENT_SCHEMA_REGISTRY_API_SECRET=<secret>"
echo

