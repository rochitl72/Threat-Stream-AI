#!/bin/bash
# Script to create Schema Registry API key using Confluent CLI

echo "=========================================="
echo "Creating Schema Registry API Key"
echo "=========================================="
echo

# Check if CLI is installed
if ! command -v confluent &> /dev/null; then
    echo "Confluent CLI not found. Installing..."
    echo
    
    # Try installation
    curl -sL --http1.1 https://cnfl.io/cli | sh -s -- latest
    
    # Add to PATH
    export PATH=$PATH:$HOME/bin
    
    # Check again
    if ! command -v confluent &> /dev/null; then
        echo "❌ Installation failed. Please install manually:"
        echo "   Visit: https://docs.confluent.io/confluent-cli/current/install.html"
        echo "   Or use: brew install confluentinc/tap/confluent (on macOS)"
        exit 1
    fi
fi

echo "✅ Confluent CLI found"
echo

# Check if logged in
if ! confluent current &> /dev/null; then
    echo "Please login to Confluent Cloud..."
    confluent login
fi

# Set environment
echo "Setting environment..."
confluent environment use env-n0grr6 2>/dev/null || echo "Environment already set"

# Create API key
echo
echo "Creating Schema Registry API key..."
echo "Resource: lsrc-rnd6q0"
echo

confluent api-key create \
  --resource lsrc-rnd6q0 \
  --description "ThreatStream AI Schema Registry" \
  --output json

echo
echo "=========================================="
echo "✅ API Key created!"
echo "=========================================="
echo
echo "Please save the API Key and Secret above."
echo "Then update your .env file with:"
echo "  CONFLUENT_SCHEMA_REGISTRY_API_KEY=<key>"
echo "  CONFLUENT_SCHEMA_REGISTRY_API_SECRET=<secret>"
