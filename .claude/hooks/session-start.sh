#!/usr/bin/env bash
# Session start hook for agentskills documentation project
echo '{"async":true,"asyncTimeout":15000}'

# Check if Mintlify CLI is installed
if ! command -v mint &> /dev/null; then
  echo "Mintlify CLI not installed. Install with: npm i -g mint"
fi
