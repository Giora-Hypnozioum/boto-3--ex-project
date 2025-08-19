#!/bin/bash

# ===============================
# AWS VPC Lab Automation Setup
# ===============================

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting setup...${NC}"

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(sys.version_info[:])")
PYTHON_MAJOR=$(python3 -c "import sys; print(sys.version_info[0])")
PYTHON_MINOR=$(python3 -c "import sys; print(sys.version_info[1])")

if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 7 ]; }; then
    echo -e "${RED}Python 3.7+ is required. Found Python $PYTHON_MAJOR.$PYTHON_MINOR${NC}"
    exit 1
fi

echo -e "${GREEN}Python version is compatible: $PYTHON_VERSION${NC}"

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo -e "${RED}requirements.txt not found!${NC}"
    exit 1
fi

# Setup fake aws.cfg if not exists
if [ ! -f "aws.cfg" ]; then
    echo -e "${YELLOW}Creating fake aws.cfg for testing...${NC}"
    cat > aws.cfg <<EOL
[default]
aws_access_key_id = AKIAFAKEEXAMPLE12345
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYFAKEKEYEXAMPLE
region = il-central-1
EOL
    echo -e "${GREEN}Fake aws.cfg created.${NC}"
else
    echo -e "${GREEN}aws.cfg already exists. Skipping creation.${NC}"
fi

echo -e "${GREEN}Setup complete!${NC}"
echo -e "${YELLOW}Activate the virtual environment with: source venv/bin/activate${NC}"
echo -e "${YELLOW}Then run automation: python3 vpc_automation.py${NC}"
