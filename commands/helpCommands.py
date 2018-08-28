#
# Help Commands
#
import os
import requests
import shutil

# Handles any commands that are prefixed with 'bot'
def handle_help_command(command, user, channel, slack_client):
    commands = command.split()
    if len(commands) < 2:
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text="Current supported 'help' commands:\nserver, bot, weather.",
            icon_emoji=':robot_face:'
        )
    elif commands[1] == 'server':
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text="Current supported 'server' commands:\nstart, stop, restart, backup, nuke.",
            icon_emoji=':robot_face:'
        )
    elif commands[1] == 'bot':
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text="Current supported 'bot' commands:\nrestart, update, version, stop*, evil.",
            icon_emoji=':robot_face:'
        )
    elif commands[1] == 'weather':
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text="Current supported 'weather' commands:\ncurrent, daily.",
            icon_emoji=':robot_face:'
        )
    else:
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text="Help command not found.\nRespond with only 'help' for a list of help commands.",
            icon_emoji=':robot_face:'
        )
    return 'success'
