#!/bin/bash
#
# Quick script to start Nuke license server and launch Nuke
# Use this every time you want to run Nuke
#

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Starting Nuke License Server...${NC}"
echo ""

# Check license server status
echo "Checking license server status..."
sudo /usr/local/foundry/LicensingTools7.1/FoundryLicenseUtility -s status -t RLM

# Start license server
echo ""
echo "Starting license server..."
sudo /usr/local/foundry/LicensingTools7.1/FoundryLicenseUtility -s start -t RLM

# Verify status
echo ""
echo "Verifying license server status..."
sudo /usr/local/foundry/LicensingTools7.1/FoundryLicenseUtility -s status -t RLM

echo ""
echo -e "${GREEN}License server started!${NC}"
echo ""

# Find Nuke installation
NUKE_PATHS=(
    "/opt/Nuke14.0v2"
    "/opt/Nuke14.0v2"
    "/opt/Nuke*"
)

NUKE_PATH=""
for path in "${NUKE_PATHS[@]}"; do
    if [ -d "$path" ]; then
        NUKE_PATH="$path"
        break
    fi
done

# Try to find any Nuke installation
if [ -z "$NUKE_PATH" ]; then
    NUKE_PATH=$(find /opt -maxdepth 1 -type d -name "Nuke*" 2>/dev/null | head -1)
fi

if [ -z "$NUKE_PATH" ]; then
    echo -e "${YELLOW}Could not find Nuke installation. Please specify the path:${NC}"
    read -p "Nuke installation path: " NUKE_PATH
fi

if [ -d "$NUKE_PATH" ]; then
    echo ""
    echo -e "${GREEN}Starting Nuke from: $NUKE_PATH${NC}"
    cd "$NUKE_PATH"
    
    # Find Nuke executable
    NUKE_EXE=$(find . -maxdepth 1 -type f -name "Nuke*" -executable | head -1)
    if [ -n "$NUKE_EXE" ]; then
        ./"$(basename "$NUKE_EXE")" &
        echo -e "${GREEN}Nuke is starting!${NC}"
    else
        echo -e "${YELLOW}Could not find Nuke executable in $NUKE_PATH${NC}"
        echo "Please run Nuke manually from the installation directory."
    fi
else
    echo -e "${YELLOW}Nuke path not found: $NUKE_PATH${NC}"
    echo "Please run Nuke manually from the installation directory."
fi

