#!/usr/bin/env bash

print_start () {
    echo "[ ] $1"
}

print_success () {
    echo "[X] Done!"
}

print_error () {
    echo "$(tput setaf 1)$(tput bold)Error:$(tput setaf 7) $1"
    echo "Exiting...$(tput sgr0)"
    exit 1
}

is_root () {
    [[ $EUID -eq 0 ]] && return 1 || return 0
}

has_systemd () {
    [[ $(pidof systemd) -ne 0 ]] && return 1 || return 0
}

prompt_yn () {
    local choice

    while [[ ! $choice =~ ^[YyNn]$ ]];
    do
        read -p "$1 [Y/n]: " -n 1 -r choice
    done

    [[ $choice =~ ^[Yy\n]$ ]] && return 1 || return 0
}
