#
# Server Commands
#
import os
import re
import requests
import shutil
from datetime import datetime
import errno
import time

from config_util import get_project, get_slack_server_channel, get_display, load_config, calculate

# Handles any commands that are prefixed with 'server'
def handle_server_command(command, user, channel, adminId, homeId, slack_client):
	commands = command.split()
	if len(commands) < 2 or commands[1] == 'help':
		slack_help_response(slack_client, channel)
	elif commands[1] == 'start' or commands[1] == 'stop' or commands[1] == 'restart' or commands[1] == 'build':
		params = ""
		for param in commands[3:]:
			params += " %s" % param
		calculate()
		server_cycle(commands[1], commands[2], params, slack_client)
	elif commands[1] == 'configure':
		calculate()
	else:
		slack_help_response(slack_client, channel)

def server_cycle(command, services, params, slack_client):
	# Update (Git Pull)
	if '-pull' in params:
		project_git_pull()

	# Stop
	if command == 'stop' or command == 'restart':
		run_command_for_services(services, 'docker-compose down', slack_client)

	# Purge Dockers
	if '-purge' in params:
		purge_docker()

	# Build
	if command == 'build' or command == 'start' or command == 'restart':
		result = run_command_for_services(services, 'docker-compose build', slack_client)
		if result == False:
			return 'error'

	# Start
	if command == 'start' or command == 'restart':
		start_services_terminals(services, slack_client)

def start_services_terminals(services, slack_client):
	channel = load_config()['slack']['channels']['server']
	slack_client.api_call(
		"chat.postMessage",
		channel=channel['id'],
		text="Beginning 'docker-compose up' for %s" % (services),
		icon_emoji=':robot_face:'
	)
	project = get_project()
	if services == 'all':
		services = project['services']
	else:
		names = re.split(',', services)
		services = []
		for service in project['services']:
			if service['name'] in names:
				services.append(service)
	errors = []
	t_width = project['t_size']['width']
	t_height = project['t_size']['height']
	window = get_display()['window']
	for service in services:
		geometry = "%sx%s+%s+%s" % (t_width, t_height, (service['t_x'] + window['leftPadding']), (service['t_y'] + window['topPadding']))
		command = 'cd %s/%s; %s' % (project['dir'], service['dir'], 'docker-compose up; sleep 20; exit; exec $SHELL')
		script = 'sudo gnome-terminal --geometry %s -- sh -c "%s"' % (geometry, command)
		slack_client.api_call(
			"chat.postMessage",
			channel=channel['id'],
			text="Beginning 'docker-compose up' for %s" % (service['name']),
			icon_emoji=':robot_face:'
		)
		if os.system(script) != 0:
			errors.append(service['name'])
			slack_client.api_call(
				"chat.postMessage",
				channel=channel['id'],
				text="Error running 'docker-compose up' for %s" % (service['name']),
				icon_emoji=':robot_face:'
			)
		else:
			slack_client.api_call(
				"chat.postMessage",
				channel=channel['id'],
				text="Successful 'docker-compose up' for %s" % (service['name']),
				icon_emoji=':robot_face:'
			)
	if len(errors) != 0:
		channel = get_slack_server_channel()
		slack_client.api_call(
			"chat.postMessage",
			channel=channel['id'],
			text="Error running 'docker-compose up' for %s" % (errors),
			icon_emoji=':robot_face:'
		)
		return False
	else:
		slack_client.api_call(
			"chat.postMessage",
			channel=channel['id'],
			text="Successful ran 'docker-compose up'",
			icon_emoji=':robot_face:'
		)
		return True

def run_command_for_services(services, command, slack_client):
	channel = load_config()['slack']['channels']['server']
	slack_client.api_call(
		"chat.postMessage",
		channel=channel['id'],
		text="Beginning '%s' for %s" % (command, services),
		icon_emoji=':robot_face:'
	)
	print('Running command: %s' % command)
	project = get_project()
	if services == 'all':
		services = project['services']
	else:
		names = re.split(',', services)
		services = []
		for service in project['services']:
			if service['name'] in names:
				services.append(service)
	errors = []
	for service in services:
		script = 'cd %s/%s; %s' % (project['dir'], service['dir'], command)
		slack_client.api_call(
			"chat.postMessage",
			channel=channel['id'],
			text="Beginning '%s' for %s" % (command, service['name']),
			icon_emoji=':robot_face:'
		)
		if os.system(script) != 0:
			errors.append(service['name'])
			slack_client.api_call(
				"chat.postMessage",
				channel=channel['id'],
				text="Error running '%s' for %s" % (command, service['name']),
				icon_emoji=':robot_face:'
			)
		else:
			slack_client.api_call(
				"chat.postMessage",
				channel=channel['id'],
				text="Successful '%s' for %s" % (command, service['name']),
				icon_emoji=':robot_face:'
			)
	if len(errors) != 0:
		channel = get_slack_server_channel()
		slack_client.api_call(
			"chat.postMessage",
			channel=channel['id'],
			text="Error running '%s' for %s" % (command, errors),
			icon_emoji=':robot_face:'
		)
		return False
	else:
		slack_client.api_call(
			"chat.postMessage",
			channel=channel['id'],
			text="Successful ran '%s'" % (command),
			icon_emoji=':robot_face:'
		)
		return True

def project_git_pull():
	print('Git Pull')
	project = get_project()
	os.system('cd ../%s; git pull' % project['dir'])

def purge_docker():
	print('Docker Purge')
	os.system('docker stop $(docker ps -a -q)')
	os.system('docker rm $(docker ps -a -q)')
	os.system('docker system prune --force')

def slack_help_response(slack_client, channel):
	slack_client.api_call(
		"chat.postMessage",
		channel=channel,
		text="Current supported 'server' format: 'server <command> <services> <params>'\ncommands: build, stop, start, restart\nservices: all, service1,service2\nparams: -pull, -purge",
		icon_emoji=':robot_face:'
	)
