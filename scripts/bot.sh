#!/bin/sh
printf "Starting DevBot...\n"

# Constant Variables
keyFile="../.key.txt"

# Check if instance of bot is running, if so stop it
result=$(ps -f -C python | grep 'devBot.py')
if [ "$result" != "" ]; then
	sudo pkill -9 -f devBot.py
else
	echo "No Instance"
fi

# Read token from .key.txt
while read -r token; do
	echo $token
done < "$keyFile"

# Construct start script to run in terminal
script="cd ..; source env/bin/activate; export SLACK_BOT_TOKEN='$token'; python devBot.py"
sudo gnome-terminal -- bash -c "${script}; sleep 10; exit; exec $SHELL"
