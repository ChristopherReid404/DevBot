#
# Bot Commands
#
import os
import requests
import shutil
import time

VERSION="v1.0.6"

# Handles any commands that are prefixed with 'bot'
def handle_bot_command(command, user, channel, adminId, homeId, slack_client):
    commands = command.split()
    if len(commands) < 2:
        return 'missing'
    elif commands[1] == 'update':
        return update_bot(user, channel, adminId, homeId, slack_client)
    elif commands[1] == 'restart':
        return restart_bot(user, channel, adminId, homeId, slack_client)
    elif commands[1] == 'stop':
        return stop_bot(user, channel, adminId, slack_client)
    elif commands[1] == 'version':
        return bot_version(channel, slack_client)
    elif commands[1] == 'evil':
        return evil_bot(channel, slack_client)

    return 'missing'

# Updates the bot
def update_bot(user, channel, adminId, homeId, slack_client):
    if user == adminId or channel == homeId:
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text="Attempting Update...",
            icon_emoji=':robot_face:'
        )
        # os.system("sh -c 'cd ../; git clean -fd; git pull;'")
        os.system("sh -c 'git clean -fd; git pull;'")
        time.sleep(3)
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text="Update Completed...",
            icon_emoji=':robot_face:'
        )
        return restart_bot(user, channel, adminId, homeId, slack_client)
    else:
        return 'unauthorized'

# Stops the bot
def stop_bot(user, channel, adminId, slack_client):
    if user == adminId:
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text="Attempting Shutdown...",
            icon_emoji=':robot_face:'
        )
        return 'shutdown'
    else:
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text="Permission denied, only the Admin call this command.",
            icon_emoji=':robot_face:'
        )
        return 'error'

# Restarts the bot
def restart_bot(user, channel, adminId, homeId, slack_client):
    if user == adminId or channel == homeId:
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text="Attempting Restart...",
            icon_emoji=':robot_face:'
        )
        os.system("gnome-terminal -- sh -c 'cd scripts; sleep 3; sh bot.sh; exit'")
        return 'shutdown'
    else:
        return 'unauthorized'


# Version of the bot
def bot_version(channel, slack_client):
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text="Running: " + VERSION,
        icon_emoji=':robot_face:'
    )

# Evil bot
def evil_bot(channel, slack_client):
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text="MUUUWAHAhAHAHA!",
        icon_emoji=':robot_face:'
    )

