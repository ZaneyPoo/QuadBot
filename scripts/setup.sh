#!/usr/bin/env bash 

print_start () {
    echo "[ ] $1"
}

print_success () {
    echo "[X] Done!"
}

print_error () { 
    echo "$(tput setaf 1)$(tput bold)Error:$(tput setaf 7) $1"
    echo "Exiting... $(tput sgr0)"
    exit 1
}

pip install -r ./requirements.txt || print_error "$DEPEND_ERROR"
print_success
