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

is_root () {
    if [[ $EUID -eq 0 ]]; then
        true 
    else 
        false 
    fi
}

has_systemd () {
    if [[ $(pidof systemd) -ne 0 ]]; then 
        true
    else 
        false
    fi
}

prompt_yn () {
    local choice
    read -d '' -p "$1 [y/N]: " -n 1 -s -r choice 

    if [[ $choice =~ ^[Yy]$ ]]; then 
        true
    else
        false
    fi
}
