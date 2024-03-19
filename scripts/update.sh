#!/usr/bin/env bash

if [ "$EUID" -ne 0 ]; then
    echo "$(tput setaf 1)$(tput bold)Error: $(tput setaf 7)please run as root."
    exit 1
fi


git switch main
git pull

echo "$(tput bold)Restarting KBot..."
systemctl restart kbot.service
