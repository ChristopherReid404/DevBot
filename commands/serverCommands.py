#
# Server Commands
#
import os
import requests
import shutil
from datetime import datetime
import errno
import time

# Handles any commands that are prefixed with 'server'
def handle_server_command(command, user, channel, adminId, homeId, slack_client):
    action = ""
    params = ""
    for index, param in enumerate(command.split(), start=0):   # default is zero
        if index > 1:
            params += param + " "
        else:
            action = param
    if action == 'start' or action == 'stop' or action == 'restart':
        return server_service(action, params, user, channel, adminId, homeId, slack_client)
    elif action == 'nuke':
        return nuke_server(channel, slack_client)
    elif action == 'backup':
        return backup_server(params, user, channel, adminId, homeId, slack_client)
    else:
        return 'missing'


def server_service(action, params, user, channel, adminId, homeId, slack_client):
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text="Attempting to " + action + " Server...",
        icon_emoji=':robot_face:'
    )
    script="gnome-terminal -- sh -c 'cd scripts; sh project.sh " + action + " " + params + "; exit'"
    os.system(script)

    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text="Successfully Server " + action + ".",
        icon_emoji=':robot_face:'
    )
    if '-bot' in params:
        return 'shutdown'
    else:
        return 'success'

def nuke_server(channel, slack_client):
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text="Attempting to nuke Server...",
        icon_emoji=':robot_face:'
    )
    script="gnome-terminal -- sh -c 'cd scripts; sh nuke.sh; exit'"
    os.system(script)

    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text="Successfully nuked Server.",
        icon_emoji=':robot_face:'
    )
    return 'success'

def backup_server(commands, user, channel, adminId, homeId, slack_client):
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text='Attempting Server Backup...',
        icon_emoji=':robot_face:'
    )
    date = datetime.now()
    date = date.strftime('%Y-%m-%d')
    directory = "/backups"
    with open("../.config", "r") as file:
        lines = file.readlines()
        for line in lines:
            content = line.split()
            if content[0] == '-b':
                directory = content[1]
    dest = directory + '/' + date
    
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=dest,
        icon_emoji=':robot_face:'
    )

    error = None
    if '-force' in commands:
        shutil.rmtree(dest, ignore_errors=True)
    try:
        shutil.copytree('../', dest, ignore=shutil.ignore_patterns('node_modules*', 'build*', 'bot*', '*.pyc', 'backups*'))
        script="chmod -R a+rX " + dest
        system.os(script)
    except OSError as e:
        time.sleep(10)
        if e.errno == errno.ENOTDIR:
            shutil.copy('../', dest)
        else:
            print('Directory not copied. Error %s' % e)
            error = e
    if error == None:
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text='Server Successfully Backed up.',
            icon_emoji=':robot_face:'
        )
        return 'success'
    else:
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text='Server Error Backing up: %s' % error,
            icon_emoji=':robot_face:'
        )
        return 'error'
