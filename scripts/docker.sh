#!/bin/sh
echo "$0 Docker Service\n"
# (1) Command - [ start, stop, restart ]
# (2) Directory - [ eg. project/frontEnd, project/microService/authService ]
# (3) Delay? - [ eg. 5, 30, 60 ]
# (#) Args - [ -destroy ]

# Initalize Param Variables
destroy="false"
for var in "$@"; do
    if [ "$var" = "-destroy" ]; then destroy="true";
fi; done

# Stop current instance, if needed
if [ "$1" = "stop" -o "$1" = "restart" ]; then
    sh -c "cd ../../$2; sudo docker-compose stop"
fi

# Delay, if needed, doubled if destroyed
if [ "$1" = "start" -o "$1" = "restart" ]; then
    if [ "$3" != "" ]; then
        if [ "$3" != "-destroy" ]; then
            echo "Sleeping for $3 seconds..."
            sleep $3
            if $destroy; then
            sleep $3
            fi
        fi
    fi
fi

# Destroys current instance, if needed
if $destroy; then
    sh -c "cd ../../$2; sudo docker-compose down"
fi

# Start instance, if needed
if [ "$1" = "start" -o "$1" = "restart" ]; then
    sh -c "cd ../../$2; docker-compose build; docker-compose up; exit"
fi
