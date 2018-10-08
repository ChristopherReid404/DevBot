import os
import time
import re
import requests
import json
from datetime import datetime
from slackclient import SlackClient
import fileinput
import logging

from commands.serverCommands import handle_server_command
from commands.botCommands import handle_bot_command
from commands.weatherCommands import handle_weather_command
from commands.helpCommands import handle_help_command
from commands.config_util import load_config, save_config

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

# pythonBot's user ID in Slack: value is assigned after the bot starts up
botId = None
homeId = None
adminId = None

# runtime variables
running = True

# commands
SERVER_COMMAND = "server"
BOT_COMMAND = "bot"
WEATHER_COMMAND = "weather"
HELP_COMMAND = "help"

# constants
RTM_READ_DELAY = 1 # 1 sesconds delay between reading from RTM
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

def handle_command(command, channel, user):
    """
        Excutes the bot command in the command is known
    """
    # Default response is help text for user
    default_response = "Not sure what you mean. Try *{}*.".format(HELP_COMMAND)

    # Finds and excutes the given command, filling in respose
    response = None
    # This is where you start to implement more commands!
    if command.startswith(SERVER_COMMAND):
        if user == adminId or channel == homeId:
            response = handle_server_command(command, user, channel, adminId, homeId, slack_client)
        else:
            response = 'unauthorized'
    elif command.startswith(BOT_COMMAND):
        response = handle_bot_command(command, user, channel, adminId, homeId, slack_client)
    elif command.startswith(WEATHER_COMMAND):
        response = handle_weather_command(command, user, channel, slack_client)
    elif command.startswith(HELP_COMMAND):
        response = handle_help_command(command, user, channel, slack_client)
    else:
        response = 'missing'

    if response != 'success':
        if response == 'unauthorized':
            slack_client.api_call(
                "chat.postMessage",
                channel=channel,
                text="Un-Authorized: Retry from the Home Channel for oversight.",
                icon_emoji=':robot_face:'
            )
        return response
    else:
        return None

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot
        commands.  If a bot command is found, this function returns a tuple
        of command and channel.  If its not found, then this function returns
        None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == botId:
                return message, event["channel"], event["user"]
    return None, None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in
        message text and returns the user ID which was mentioned. If there is
        no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, second contains the message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def fetch_channel_ids():
    config = load_config()
    c_channels = config['slack']['channels']
    channels_call = slack_client.api_call("channels.list")
    if channels_call.get('ok'):
        channels = channels_call["channels"]
        if c_channels['home']['id'] == '':
            for c in channels:
                if c['name'] == c_channels['home']['name']:
                    c_channels['home']['id'] = c['id']
        if c_channels['report']['id'] == '':
            for c in channels:
                if c['name'] == c_channels['report']['name']:
                    c_channels['report']['id'] = c['id']
                    Id = c['id']
        else:
            Id = c_channels['report']['id']
        if c_channels['server']['id'] == '':
            for c in channels:
                if c['name'] == c_channels['server']['name']:
                    c_channels['server']['id'] = c['id']
        config['slack']['channels'] = c_channels
        save_config(config)
        return Id
    else:
        print('Unable to load Channels')

def fetch_admin():
	with open('config.json') as data_file:
		config = json.load(data_file)
        root = config['slack']['root']
        if root['id'] == "":
            users_call = slack_client.api_call("users.list")
            if users_call.get('ok'):
                users = users_call["members"]
                for u in users:
                    if u["name"] == root['name']:
                        Id = u["id"]
                        config['slack']['root']['id'] = Id
                        with open('config.json', 'w') as data_file:
                            data_file.write(json.dumps(config, indent=2, sort_keys=True))
                        return Id
        else:
            return root['id']

if __name__ == "__main__":
    print("Attempting to connect DevBot")
    logging.info("Begin")
    if slack_client.rtm_connect(with_team_state=False):
        # Fetch Ids for Admins and Channels
        reportId = fetch_channel_ids()
        adminId = fetch_admin()
        # Read bot's user ID by calling Web API method `auth.test`
        botId = slack_client.api_call("auth.test")["user_id"]
        print("DevBot connected and running!")
        slack_client.api_call(
            "chat.postMessage",
            channel=reportId,
            text="Online ~ " + datetime.now().strftime('%I:%M:%S %p'),
            icon_emoji=':robot_face:'
        )
        try:
            while running:
                command, channel, user = parse_bot_commands(slack_client.rtm_read())
                if command:
                    print("(" + user + ") attempting: " + command)
                    result = handle_command(command, channel, user)
                    # Some commands require returning a result to be set
                    if result != None:
                        if result == 'shutdown':
                            running = False
                        else:
                            slack_client.api_call(
                                "chat.postMessage",
                                channel=channel,
                                text="Error with Command: (' " + result + " ') - " + command + " (" + user + ").",
                                icon_emoji=':robot_face:'
                            )
                    print('Command Complete.')
                time.sleep(RTM_READ_DELAY)
            slack_client.api_call(
                "chat.postMessage",
                channel=reportId,
                text="Shutdown ~ " + datetime.now().strftime('%I:%M:%S %p'),
                icon_emoji=':robot_face:'
            )
        except Exception, e:
            slack_client.api_call(
                "chat.postMessage",
                channel=reportId,
                text="Crashing ~ " + datetime.now().strftime('%I:%M:%S %p') + " -> " + str(e),
                icon_emoji=':robot_face:'
            )
            os.system("gnome-terminal -- sh -c 'cd scripts; sleep 3; sh bot.sh; exit'")
            slack_client.api_call(
                "chat.postMessage",
                channel=reportId,
                text="Attempting Auto-Restart...",
                icon_emoji=':robot_face:'
            )
    else:
        print("Connection failed. Exception traceback printed above.")
