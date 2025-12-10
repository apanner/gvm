#!/bin/bash
#
# Nuke Installation Script - Standalone Version
# This script automates the Nuke installation process on Linux
#
# Usage: ./install_nuke_standalone.sh
#        You will be prompted for file paths during execution
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${GREEN}[STEP $1]${NC} $2"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Check if running as root (we'll use sudo instead)
if [ "$EUID" -eq 0 ]; then 
    print_warning "Running as root. It's better to run as regular user and use sudo."
fi

echo "=========================================="
echo "Nuke Installation Script"
echo "=========================================="
echo ""

# Prompt for file paths
print_info "Please provide the paths to the required files:"
echo ""

read -p "Path to Nuke .run file: " NUKE_RUN
if [ ! -f "$NUKE_RUN" ]; then
    print_error "Nuke .run file not found: $NUKE_RUN"
    exit 1
fi

read -p "Path to FLT7 .tgz file: " FLT7_TGZ
if [ ! -f "$FLT7_TGZ" ]; then
    print_error "FLT7 .tgz file not found: $FLT7_TGZ"
    exit 1
fi

read -p "Path to rlm.foundry file: " RLM_FOUNDRY
if [ ! -f "$RLM_FOUNDRY" ]; then
    print_error "rlm.foundry file not found: $RLM_FOUNDRY"
    exit 1
fi

read -p "Path to foundry.set file: " FOUNDRY_SET
if [ ! -f "$FOUNDRY_SET" ]; then
    print_error "foundry.set file not found: $FOUNDRY_SET"
    exit 1
fi

read -p "Path to xf_foundry.lic file: " LICENSE_FILE
if [ ! -f "$LICENSE_FILE" ]; then
    print_error "License file not found: $LICENSE_FILE"
    exit 1
fi

read -p "Installation path (default: /opt): " INSTALL_PATH
INSTALL_PATH=${INSTALL_PATH:-/opt}

read -p "Nuke version (default: 14.0v2): " NUKE_VERSION
NUKE_VERSION=${NUKE_VERSION:-14.0v2}

echo ""
print_info "Installation summary:"
echo "  Nuke installer: $NUKE_RUN"
echo "  FLT7 archive: $FLT7_TGZ"
echo "  rlm.foundry: $RLM_FOUNDRY"
echo "  foundry.set: $FOUNDRY_SET"
echo "  License file: $LICENSE_FILE"
echo "  Install path: $INSTALL_PATH"
echo "  Nuke version: $NUKE_VERSION"
echo ""

read -p "Continue with installation? (y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "Installation cancelled."
    exit 0
fi

# Step 1-4: Install Nuke
print_step "1-4" "Installing Nuke..."
NUKE_DIR=$(dirname "$NUKE_RUN")
NUKE_FILE=$(basename "$NUKE_RUN")

cd "$NUKE_DIR"
sudo chmod a+rwx "$NUKE_FILE"
print_info "Running Nuke installer. Please follow the installation wizard."
print_warning "IMPORTANT: Install Nuke to $INSTALL_PATH folder"
sudo ./"$NUKE_FILE" || sudo bash "$NUKE_FILE"

# Step 5-12: Install FLT7 License Server
print_step "5-12" "Installing FLT7 License Server..."
FLT7_DIR=$(dirname "$FLT7_TGZ")
cd "$FLT7_DIR"

# Extract FLT7
FLT7_ARCHIVE=$(basename "$FLT7_TGZ")
print_info "Extracting FLT7 archive..."
tar xvzf "$FLT7_ARCHIVE"

# Find extracted directory
EXTRACTED_DIR=$(find . -maxdepth 1 -type d -name "FLT7*" | head -1)
if [ -z "$EXTRACTED_DIR" ]; then
    print_error "Could not find extracted FLT7 directory"
    exit 1
fi

print_info "Found extracted directory: $EXTRACTED_DIR"
cd "$EXTRACTED_DIR"
sudo chmod a+rwx ./install.sh
print_info "Running FLT7 installer..."
sudo ./install.sh || sudo bash install.sh

echo ""
print_warning "=========================================="
print_warning "MANUAL STEP REQUIRED"
print_warning "=========================================="
print_info "Please open Firefox (disable VPN if using one) and navigate to one of these URLs:"
echo "  http://127.0.0.1:4102"
echo "  http://127.0.0.1:5053"
echo "  http://127.0.0.1:4101"
echo ""
print_info "Once you see the 'Reprise License Server Administration' page:"
print_info "1. Click 'Shutdown' button on the left side"
print_info "2. Click 'SHUT DOWN SERVER'"
print_info "3. Don't change anything in 'ISV' (should be '-all' by default)"
echo ""
read -p "Press Enter when you have shut down the server..."

# Step 13-22: Copy crack files and license
print_step "13-22" "Copying crack files and license..."

# Remove existing files
print_info "Removing existing license files..."
sudo rm -f /usr/local/foundry/RLM/rlm.foundry
sudo rm -f /usr/local/foundry/LicensingTools7.1/bin/RLM/rlm.foundry
sudo rm -f /usr/local/foundry/RLM/foundry.set
sudo rm -f /usr/local/foundry/LicensingTools7.1/bin/RLM/foundry.set

# Copy crack files
print_info "Copying rlm.foundry..."
sudo cp "$RLM_FOUNDRY" /usr/local/foundry/RLM/rlm.foundry
sudo cp "$RLM_FOUNDRY" /usr/local/foundry/LicensingTools7.1/bin/RLM/rlm.foundry

print_info "Copying foundry.set..."
sudo cp "$FOUNDRY_SET" /usr/local/foundry/RLM/foundry.set
sudo cp "$FOUNDRY_SET" /usr/local/foundry/LicensingTools7.1/bin/RLM/foundry.set

# Copy license file
print_info "Copying license file..."
sudo cp "$LICENSE_FILE" /usr/local/foundry/RLM/xf_foundry.lic

# Step 23-25: Start license server
print_step "23-25" "Starting license server..."
print_info "Checking license server status..."
sudo /usr/local/foundry/LicensingTools7.1/FoundryLicenseUtility -s status -t RLM

print_info "Starting license server..."
sudo /usr/local/foundry/LicensingTools7.1/FoundryLicenseUtility -s start -t RLM

print_info "Verifying license server status..."
sudo /usr/local/foundry/LicensingTools7.1/FoundryLicenseUtility -s status -t RLM

echo ""
echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}Installation completed successfully!${NC}"
echo -e "${GREEN}==========================================${NC}"
echo ""
print_warning "IMPORTANT: Every time you want to run Nuke, execute these commands:"
echo "  sudo /usr/local/foundry/LicensingTools7.1/FoundryLicenseUtility -s status -t RLM"
echo "  sudo /usr/local/foundry/LicensingTools7.1/FoundryLicenseUtility -s start -t RLM"
echo "  sudo /usr/local/foundry/LicensingTools7.1/FoundryLicenseUtility -s status -t RLM"
echo ""
print_info "Then run Nuke from: $INSTALL_PATH/Nuke$NUKE_VERSION/"
echo ""

read -p "Do you want to start Nuke now? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Starting Nuke..."
    cd "$INSTALL_PATH/Nuke$NUKE_VERSION/"
    ./Nuke$NUKE_VERSION &
    print_info "Nuke should be starting now!"
fi

echo ""
print_info "Installation script completed!"

