#!/bin/bash
# Install Confluent CLI and create Schema Registry API key

echo "Installing Confluent CLI..."
echo

# Install CLI
curl -sL --http1.1 https://cnfl.io/cli | sh -s -- latest

# Add to PATH
export PATH=$PATH:$HOME/bin

# Check if installed
if command -v confluent &> /dev/null; then
    echo "✅ Confluent CLI installed successfully"
    echo
    echo "Next steps:"
    echo "1. Login: confluent login"
    echo "2. Create Schema Registry API key:"
    echo "   confluent api-key create --resource lsrc-rnd6q0 --description 'ThreatStream AI Schema Registry'"
    echo
else
    echo "❌ Installation failed. Try manual installation:"
    echo "   Visit: https://docs.confluent.io/confluent-cli/current/install.html"
    echo
fi


