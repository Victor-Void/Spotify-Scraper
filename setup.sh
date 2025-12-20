#!/bin/bash

# Spotify Playlist Scraper - Setup Script
# This script automates the environment setup on Linux.

set -e # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}   Spotify Playlist Scraper - Setup Window   ${NC}"
echo -e "${BLUE}==================================================${NC}"

# 1. Check for Python 3
echo -e "\n${YELLOW}Step 1: Checking for Python 3...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ Found $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Python 3 is not installed. Please install it with: sudo apt install python3 python3-venv${NC}"
    exit 1
fi

# 2. Check for Firefox
echo -e "\n${YELLOW}Step 2: Checking for Firefox...${NC}"
if command -v firefox &> /dev/null; then
    FIREFOX_VERSION=$(firefox --version)
    echo -e "${GREEN}✓ Found $FIREFOX_VERSION${NC}"
else
    echo -e "${RED}✗ Firefox is not installed. Please install it with: sudo apt install firefox${NC}"
    exit 1
fi

# 3. Create virtual environment
echo -e "\n${YELLOW}Step 3: Creating virtual environment (venv)...${NC}"
if [ -d "venv" ]; then
    echo -e "${BLUE}! Virtual environment 'venv' already exists. Skipping creation.${NC}"
else
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created successfully.${NC}"
fi

# 4. Install dependencies
echo -e "\n${YELLOW}Step 4: Installing dependencies...${NC}"
source venv/bin/activate
if [ -f "requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed successfully.${NC}"
else
    echo -e "${RED}✗ requirements.txt not found!${NC}"
    exit 1
fi

echo -e "\n${BLUE}==================================================${NC}"
echo -e "${GREEN}   Setup Complete!${NC}"
echo -e "${BLUE}==================================================${NC}"
echo -e "\nTo start the scraper, run:"
echo -e "${BLUE}source venv/bin/activate${NC}"
echo -e "${BLUE}python main.py${NC}"
echo -e "\n${YELLOW}Note: Make sure Firefox is closed before running the script!${NC}"
