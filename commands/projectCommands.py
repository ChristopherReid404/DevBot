#
# Project Commands
#
import os
import shutil
from datetime import datetime
import errno
import time

# Handles any commands that are prefixed with 'server'
def handle_project_command(command, user, channel, adminId, homeId, slack_client):
	commands = command.split()
	if len(commands) < 2:
		slack_client.api_call(
			"chat.postMessage",
			channel=channel,
			text="Current supported 'project' commands:\nbackup",
			icon_emoji=':robot_face:'
		)
	elif commands[1] == 'backup':
		return backup_server(params, user, channel, adminId, homeId, slack_client)
	else:
		slack_client.api_call(
			"chat.postMessage",
			channel=channel,
			text="Error: Command not found.\nCurrent supported 'project' commands:\nbackup",
			icon_emoji=':robot_face:'
		)
		return 'missing'

def backup_project(commands, user, channel, adminId, homeId, slack_client):
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

# Will be added later with full aws deploy support
# def push_dockers(services, env, slack_client):
# 	channel = load_config()['slack']['channels']['server']
# 	slack_client.api_call(
# 		"chat.postMessage",
# 		channel=channel['id'],
# 		text="Beginning push_docker for %s" % (services),
# 		icon_emoji=':robot_face:'
# 	)
# 	run_command_for_services(services, 'docker-compose build', slack_client)
# 	project = get_project()
# 	if services == 'all':
# 		services = project['services']
# 	else:
# 		names = re.split(',', services)
# 		services = []
# 		for service in project['services']:
# 			if service['name'] in names:
# 				services.append(service)
# 	errors = []
# 	for service in services:
# 		script = 'cd %s/%s; %s %s' % (project['dir'], service['dir'], 'sh push_docker.sh', env)
# 		result = os.system(script)
# 		print('Result: %s' % result)
