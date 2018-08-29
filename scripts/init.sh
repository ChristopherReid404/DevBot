#!/bin/sh
printf "Initializing DevBot...\n"

# Set permissions of required scripts
sudo chmod 0777 bot.sh
sudo chmod 0777 docker.sh
sudo chmod 0777 init.sh
# sudo chmod 0777 ngrok.sh
sudo chmod 0777 nuke.sh
sudo chmod 0777 project.sh

# Constant Variables
configFile="../.config.txt"
keyFile="../.key.txt"

# Running ConfigFile Variable
config=""

if [ ! -f $configFile ]; then
	slackAdmin=""
	while [ "$slackAdmin" = "" ]; do
		read -p "Enter the Slack username for the admin: " slackAdmin
	done
	slackChannel=""
	while [ "$slackChannel" = "" ]; do
		read -p "Enter the Slack channel name to report to: " slackChannel
	done
	config="$config-sa $slackAdmin\n-sc $slackChannel\n"
fi

# Check if key.txt file exists
if [ ! -f $keyFile ]; then
	printf "For DevBot to operate it needs the workspace token saved to easily restart, \nthis is not commited to github, only saved locally within the 'key.txt' file"
	slackKey=""
	while [ "$slackKey" = "" ]; do
		printf "\n"
		read -p "Enter / Paste the 'Bot User OAuth Access Token' provided by Slack: " slackKey
		if [ "$slackKey" != '' ]; then
			echo $slackKey > $keyFile
		fi
	done
fi

# Check if env environment exists
if [ ! -d "../env" ]; then
	bash -c "cd ..; virtualenv env; source env/bin/activate; pip install slackclient; exit"
fi

# Create .config file
if [ ! -f $configFile ]; then
	projectDir=""
	while [ "$projectDir" = "" ]; do
		read -p "Enter the name of your project (Should be within the same folder as DevBot): " projectDir
	done
	config="$config-p $projectDir\n"
	addServices="true"
	printf "\nAdd a docker services for DevBot to control (stored in .config.txt)\n"
	while $addServices; do
		serviceDir=""
		while [ "$serviceDir" = "" ]; do
			read -p "Enter the root path to the service (eg. microService/authService): " serviceDir
		done
		config="$config-d $serviceDir\n"
		yn=""
		while [ "$yn" != "y" -a "$yn" != "n" ]; do
			read -p "Are there more services to add? (y/n): " yn
			if [ "$yn" = 'n' ]; then
				addServices="false"
			fi
		done
	done
	backupDir=""
	while [ "$backupDir" = "" ]; do
		read -p "Enter the root path to store backups (eg. /backups, /project/backups): " backupDir
	done
	config="$config-b $backupDir\n"
	echo $config > $configFile
fi

sudo chmod 0666 $configFile

printf "DevBot Initialized.\n"
