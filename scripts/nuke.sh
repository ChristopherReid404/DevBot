#!/bin/sh
echo "Nuke Services\n"

docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)

echo "Nuke Complete.\n"
