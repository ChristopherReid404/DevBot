#!/bin/sh
echo "Starting Docker(s)..."

# Constant Variables
configFile="../../.config.txt"

xt=0
yt=0
while read -r line
do
	set -- $line
	if [ "$1" = "-xt" ]; then
		xt=$2
	elif [ "$1" = "-yt" ]; then
		yt=$2
	fi
done < $configFile

echo $xt $yt

# Variables for even screen terminals on screen
LINE=`xrandr -q | grep Screen`
WIDTH=`echo ${LINE} | awk '{ print $8 }'`
HEIGHT=`echo ${LINE} | awk '{ print $10 }' | awk -F"," '{ print $1 }'`
if [ $WIDTH -gt 1920 ]; then
    WIDTH=1920 
fi
HEIGHT=$(( $HEIGHT - 20 )) # Remove bottom menu from height
WIDTH=$(( $WIDTH - 65 )) # Remove side menu from height
sw=$(( $WIDTH / $xt ))
sh=$(( $HEIGHT / $yt ))
tw=$(( $WIDTH / $xt / 10 ))
th=$(( $HEIGHT / $yt / 20 ))
left=1
top=0

project=""
while read -r line
do
	set -- $line
	if [ "$1" = "-p" ]; then
		project=$2
	elif [ "$1" = "-d" ]; then
		geometry="${tw}x${th}+$(($(($sw * $left)) + 65))+$(($(($sh * $top)) + 20))"
		if [ $left -gt 0 ]; then
			left=0
			top=$(($top + 1))
		else
			left=$(($left + 1))
		fi
		script="cd ../../../$project/$2; docker-compose up"
		echo $script
		sudo gnome-terminal --geometry $geometry -- sh -c "$script; exit; exec $SHELL"
	fi
done < $configFile

echo "Docker(s) Started."
