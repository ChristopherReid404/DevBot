#!/bin/sh
echo "$0 Global Service\n"
# (0) Command - [ start, stop, restart ]
# (#) Args - [ -pull, -destroy ]

# Constant Variables
configFile="../.config.txt"
xTerminals=2
yTerminals=3
command="$1"

# Initalize Param Variables
pull="false"; destroy=""; bot="false"
for var in "$@"; do
    if [ "$var" = "-pull" ]; then pull="true";
    elif [ "$var" = "-destroy" ]; then destroy="-destroy";
    elif [ "$var" = "-bot" ]; then bot="true";
	fi
done

project=""
# Get the command directory from config
while read -r line
do
	set -- $line
	if [ "$1" = "-p" ]; then
		project=$2
	fi
done < $configFile

# Drop changes and pull, if needed
if $pull; then
    sh -c "cd ../../$project; git clean -fd; git pull"
fi

# Variables for even screen terminals on screen
LINE=`xrandr -q | grep Screen`
WIDTH=`echo ${LINE} | awk '{ print $8 }'`
HEIGHT=`echo ${LINE} | awk '{ print $10 }' | awk -F"," '{ print $1 }'`
if [ $WIDTH -gt 1920 ]; then
    WIDTH=1920 
fi
HEIGHT=$(( $HEIGHT - 20 )) # Remove bottom menu from height
WIDTH=$(( $WIDTH - 65 )) # Remove side menu from height
sw=$(( $WIDTH / $xTerminals ))
sh=$(( $HEIGHT / $yTerminals ))
tw=$(( $WIDTH / 19 ))
th=$(( $HEIGHT / 160 ))
left=0
top=0

# Run command on each docker
while read -r line
do
	set -- $line
	if [ "$1" = "-d" ]; then
		script="sh docker.sh $command $project/$2 $3 $destroy"
		geometry="${tw}x${th}+$(($(($sw * $left)) + 65))+$(($(($sh * $top)) + 20))"
		if [ $left -gt 0 ]; then
			left=0
			top=$(($top + 1))
		else
			left=$(($left + 1))
		fi
		echo $script
		sudo gnome-terminal --geometry $geometry -- sh -c "$script; exit; exec $SHELL"
	fi
done < $configFile

# Restart bot, if needed
if $bot; then
	script="bot.sh; exit; exec $SHELL"
	sudo gnome-terminal -e "sh -c '$script'"
fi