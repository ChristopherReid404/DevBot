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
        text="Attempting to " + action + " server...",
        icon_emoji=':robot_face:'
    )
    script="cd scripts; sh project.sh " + action + " " + params
    os.system(script)

    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text="Successfully triggered server " + action + ".",
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
        text="Attempting to nuke server...",
        icon_emoji=':robot_face:'
    )
    os.system("cd scripts; sh nuke.sh")

    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text="Successfully triggered server nuke.",
        icon_emoji=':robot_face:'
    )
    return 'success'

def backup_server(commands, user, channel, adminId, homeId, slack_client):
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text='Attempting to backup server...',
        icon_emoji=':robot_face:'
    )
    date = datetime.now()
    date = date.strftime('%Y-%m-%d')
    directory = "/backups"
    project=""
    with open(".config.txt", "r") as file:
        lines = file.readlines()
        for line in lines:
            content = line.split()
            if content[0] == '-b':
                directory = content[1]
            elif content[0] == '-p':
                project = content[1]
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
        shutil.copytree("../" + project, dest, ignore=shutil.ignore_patterns('node_modules*', 'build*', 'bot*', '*.pyc', 'backups*'))
        script="chmod -R a+rX " + dest
        os.system(script)
    except OSError as e:
        if e.errno == errno.ENOTDIR:
            shutil.copy('../' + project, dest)
        else:
            error = e
        time.sleep(10)
    if error == None:
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text='Successfully server backup.',
            icon_emoji=':robot_face:'
        )
        return 'success'
    else:
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text='Error with server backup: %s' % error,
            icon_emoji=':robot_face:'
        )
        return 'error'
