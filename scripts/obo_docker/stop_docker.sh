#!/bin/sh
echo "Stopping Docker(s)..."

# Constant Variables
configFile="../../.config.txt"

project=""
while read -r line
do
	set -- $line
	if [ "$1" = "-p" ]; then
		project=$2
	elif [ "$1" = "-d" ]; then
    response=$(sh -c "cd ../../../$project/$2; sudo docker-compose stop")
		echo $2 - $response
	fi
done < $configFile

echo "Docker(s) Stopped."
