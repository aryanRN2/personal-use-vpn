#!/bin/bash

# Exit on any error
set -e

echo "Setting up VPN Project Environment..."

# Check for Homebrew
if ! command -v brew &> /dev/null; then
    echo "Homebrew is not installed. Please install it from https://brew.sh/"
    exit 1
fi

# Check and install wireguard-tools
if ! command -v wg &> /dev/null; then
    echo "Installing wireguard-tools..."
    brew install wireguard-tools
else
    echo "wireguard-tools already installed."
fi

# Check and install wireguard-go
if ! command -v wireguard-go &> /dev/null; then
    echo "Installing wireguard-go..."
    brew install wireguard-go
else
    echo "wireguard-go already installed."
fi

# Set up Python virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate venv and install requirements
echo "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Setup complete. To activate the virtual environment, run: source venv/bin/activate"
