#!/bin/bash

# Set the name of the virtual environment directory
VENV_DIR="cocktail_maker_venv"
REQUIREMENTS_FILE="requirements.lock"

# Function to activate the virtual environment
activate_venv() {
  if [ -f "$VENV_DIR/bin/activate" ]; then
    # Linux/Mac
    source "$VENV_DIR/bin/activate"
  elif [ -f "$VENV_DIR/Scripts/activate" ]; then
    # Windows
    source "$VENV_DIR/Scripts/activate"
  else
    echo "Error: Could not find the activate script."
    exit 1
  fi
}

# Check if the virtual environment already exists
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment..."
  python -m venv "$VENV_DIR"

  # Activate the virtual environment
  activate_venv

  # Install dependencies from requirements.lock if it exists
  if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Installing dependencies from $REQUIREMENTS_FILE..."
    pip install --no-cache-dir -r "$REQUIREMENTS_FILE"
  else
    echo "Error: $REQUIREMENTS_FILE not found."
    exit 1
  fi
else
  # Activate the virtual environment
  activate_venv
  echo "Virtual environment already exists. Activated."
fi
