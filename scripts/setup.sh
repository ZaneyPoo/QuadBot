#!/usr/bin/env bash 

source ./utils.sh

VENV=$(pwd)/.venv
ENV_FILE=$(pwd)/.env
USER_RW_PERMS=600

VENV_ERROR="couldn't create venv."
DEPEND_ERROR="couldn't install dependencies." 

if [[ ! -d $VENV ]];
then 
    print_start "Setting up Python's virtual environment"
    python3 -m venv "$VENV" || print_error "$VENV_ERROR"
    print_success
fi

print_start "Installing dependencies..."
source .venv/bin/activate
pip install -r ./requirements.txt || print_error "$DEPEND_ERROR"
print_success

if [[ $(has_systemd) ]];
then
    if [[ ! -e $PWD/qbot.service ]];
    then 
        print_start "Creating systemd unit file..."
        echo "$SERVICE" > qbot.service
        print_success

        print_start "Enabling service..."
        systemctl --user --now enable qbot.service
    fi
fi

if [[ ! -e $ENV_FILE ]];
then 
    print "Creating .env file..."
    read -p "Enter Discord API token: " -r -e TOKEN
    echo "DISCORD_TOKEN=$TOKEN" > "$ENV_FILE"
    chmod "$USER_RW_PERMS" .env || print_error "$CHMOD_ERROR"
    print_success

elif [[ $(stat -c "%a" "$ENV_FILE") -ne $USER_RW_PERMS ]];
then
    echo " Warning: the file permissions for your .env file aren't strict enough."
    echo " Current: $(stat -c "%A" "$ENV_FILE")"
    echo "Expected: (-rw------)"
    print_start "Setting proper permissions..."
    chmod "$USER_RW_PERMS" .env || print_error "$CHMOD_ERROR"
    print_success
fi
