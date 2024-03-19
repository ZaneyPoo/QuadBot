#!/usr/bin/env bash 

print_start () {
    echo "[ ] $1"
}

print_success () {
    echo "[X] Done!"
}

print_error () { 
    echo "Error: $1"
    echo "Exiting..."
    exit 1
}

print_start "Installing dependencies..."
pip install -q -r ./requirements.txt || print_error "$DEPEND_ERROR"
print_success
