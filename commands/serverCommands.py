#
# Server Commands
#
import os
import re
import requests
import shutil

from pprint import pprint

from datetime import datetime
import errno
import time

from utils import load_config, calculate

# Handles any commands that are prefixed with 'server'
def handle_server_command(command, user, channel, adminId, homeId, slack_client):
	commands = command.split()
	result = None
	if len(commands) <= 2 or commands[1] == 'help':
		slack_help_response(slack_client, channel)
	elif commands[1] == 'start' or commands[1] == 'stop' or commands[1] == 'restart' or commands[1] == 'build':
		params = ""
		for param in commands[3:]:
			params += " %s" % param
		result = server_cycle(commands[1], commands[2], params, channel, slack_client)
	elif commands[1] == 'test':
		result = test_services(commands[2], channel, slack_client)
	else:
		slack_help_response(slack_client, channel)
	if result != None:
		if result:
			slack_client.api_call(
				"chat.postMessage",
				channel=channel,
				text="Success: %s for %s" % (commands[1], commands[2]),
				icon_emoji=':robot_face:'
			)
		else:
			slack_client.api_call(
				"chat.postMessage",
				channel=channel,
				text="Failure: %s for %s" % (commands[1], commands[2]),
				icon_emoji=':robot_face:'
			)

def server_cycle(command, services, params, channel ,slack_client):
	slack_client.api_call(
		"chat.postMessage",
		channel=channel,
		text="Beginning %s for %s" % (command, services),
		icon_emoji=':robot_face:'
	)

	# Update (Git Pull)
	if '-pull' in params:
		project_git_pull()

	# Stop
	if command == 'stop' or command == 'restart':
		if '-hard' in params:
			run_command_for_services(services, 'docker-compose down', slack_client)
		else:
			run_command_for_services(services, 'docker-compose stop', slack_client)

	# Purge Dockers
	if '-purge' in params:
		purge_docker()

	# Build
	if command == 'build' or command == 'start' or command == 'restart':
		result = run_command_for_services(services, 'docker-compose build', slack_client)

	# Start
	if command == 'start' or command == 'restart':
		start_services_terminals(services, slack_client)

def test_services(services, channel, slack_client):
	slack_client.api_call(
		"chat.postMessage",
		channel=channel,
		text="Beginning tests for %s" % (services),
		icon_emoji=':robot_face:'
	)

	config = load_config()
	channel = config['slack']['channels']['server']
	project = config['project']
	slack_client.api_call(
		"chat.postMessage",
		channel=channel['id'],
		text="Beginning tests for %s" % (services),
		icon_emoji=':robot_face:'
	)
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
		port = service['port']
		try:
			r = requests.post("http://localhost:" + str(port),
				json={},
				headers={
					"Access-Control-Allow-Origin": "*",
					"Accept": "application/json",
					"Content-Type": "application/json"
				}
			)
			# So long as it doesn't throw, it's online.
			slack_client.api_call(
				"chat.postMessage",
				channel=channel['id'],
				text="Successful test for %s" % (service['name']),
				icon_emoji=':robot_face:'
			)
		except Exception, e:
			errors.append(service['name'])
			slack_client.api_call(
				"chat.postMessage",
				channel=channel['id'],
				text="Error running test for %s" % (service['name']),
				icon_emoji=':robot_face:'
			)
	if len(errors) != 0:
		slack_client.api_call(
			"chat.postMessage",
			channel=channel['id'],
			text="Error running tests for %s" % (errors),
			icon_emoji=':robot_face:'
		)
		return False
	else:
		slack_client.api_call(
			"chat.postMessage",
			channel=channel['id'],
			text="Successful ran tests",
			icon_emoji=':robot_face:'
		)
		return True

def start_services_terminals(services, slack_client):
	config = load_config()
	channel = config['slack']['channels']['server']
	project = config['project']

	# Calculate the needed x,y for terminals
	calculate()

	slack_client.api_call(
		"chat.postMessage",
		channel=channel['id'],
		text="Beginning 'docker-compose up' for %s" % (services),
		icon_emoji=':robot_face:'
	)
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
	window = config['display']['window']
	for service in services:
		geometry = "%sx%s+%s+%s" % (t_width, t_height, (service['t_x'] + window['leftPadding']), (service['t_y'] + window['topPadding']))
		command = 'cd %s/%s; %s' % (project['dir'], service['dir'], 'docker-compose up; exit; exec $SHELL')
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
	config = load_config()
	channel = config['slack']['channels']['server']
	project = config['project']
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
		slack_client.api_call(
			"chat.postMessage",
			channel=channel['id'],
			text="Error running '%s' for %s" % (command, errors),
			icon_emoji=':robot_face:'
		)
		return False
	else:
		return True

def project_git_pull():
	project = load_config()['project']
	os.system('cd %s; git pull' % project['dir'])

def purge_docker():
	os.system('docker stop $(docker ps -a -q)')
	os.system('docker rm $(docker ps -a -q)')
	os.system('docker system prune --force')

def slack_help_response(slack_client, channel):
	slack_client.api_call(
		"chat.postMessage",
		channel=channel,
		text="Current supported 'server' format: 'server <command> <services> <params>'\ncommands: build, stop, start, restart, test\nservices: all, service1,service2\nparams: -pull, -purge, -hard\nParams not available when running 'test'",
		icon_emoji=':robot_face:'
	)
