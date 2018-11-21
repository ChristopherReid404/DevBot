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

token=""
# Read token from .key.txt
while read -r line; do
	if [ "$line" != "" ]; then
		token=$line
	fi
done < "$keyFile"

# Construct start script to run in terminal
script="cd ..; source env/bin/activate; export SLACK_BOT_TOKEN='$token'; python devBot.py"
sudo gnome-terminal --geometry 80x8+640+0 -- bash -c "${script}; echo 'Closing...'; sleep 5; exit; exec $SHELL"
