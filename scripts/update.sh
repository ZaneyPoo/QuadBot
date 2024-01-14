#!/usr/bin/env bash

source ./utils.sh

[[ ! $is_root ]] && print_error "please run as root."

git switch main
git pull

print_start "Restarting QuadBot..."
systemctl --user restart qbot.service || print_error "couldn't restart QuadBot service."
print_success
