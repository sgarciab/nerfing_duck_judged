#!/bin/bash
set -e

# Function to check version
version_gt() { test "$(printf '%s\n' "$@" | sort -V | head -n 1)" != "$1"; }

# Check for Python 3.10+
REQUIRED_VERSION="3.10"
PYTHON_BIN="python3"

if ! command -v $PYTHON_BIN &> /dev/null; then
    echo "Error: $PYTHON_BIN could not be found."
    exit 1
fi

CURRENT_VERSION=$($PYTHON_BIN -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$CURRENT_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
     echo "Python version $CURRENT_VERSION detected (>= $REQUIRED_VERSION). Good."
else
    echo "Error: Python $REQUIRED_VERSION+ is required. Found $CURRENT_VERSION."
    exit 1
fi

# Create venv
VENV_DIR=".venv"
ACTIVATE_SCRIPT="$VENV_DIR/bin/activate"

if [ -f "$ACTIVATE_SCRIPT" ]; then
    echo "Virtual environment already exists in $VENV_DIR."
else
    if [ -d "$VENV_DIR" ]; then
        echo "Found incomplete virtual environment in $VENV_DIR. Cleaning up..."
        rm -rf "$VENV_DIR"
    fi
    
    echo "Creating virtual environment in $VENV_DIR..."
    if $PYTHON_BIN -m venv $VENV_DIR; then
        echo "Virtual environment created successfully."
    else
        echo "ERROR: Failed to create virtual environment."
        echo "This is closely related to missing system dependencies on Linux."
        echo "Please try running the following command:"
        echo ""
        echo "    sudo apt install python3.12-venv"
        echo ""
        exit 1
    fi
fi

# Create requirements.txt if not exists
if [ ! -f "requirements.txt" ]; then
    echo "Creating empty requirements.txt..."
    touch requirements.txt
fi

echo ""
echo "Setup complete. To activate the virtual environment, run:"
echo "source $VENV_DIR/bin/activate"
