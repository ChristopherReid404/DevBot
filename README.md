# DevBot

DevBot allows simply control over a project setup to use docker to help speed development when a local server is required.

DevBot can start / stop / restart / destroy a group of docker containers along with handling the overal project updating (github) and local backups.  There are a few extra commands added to simply give more features ( weather )

Any commands made that effect the server or bot must come from the admin or the DevBot's home channel, witht he exception of stopping the bot can only be done by the admin.

## Requirement

DevBot was built for a Linux hosting environment, no current plans for Windows support.

- Linux ( Ubuntu 18.04 )
- Python ( v2.7+ )
- Docker ( v17.21.1-ce )
- docker-compose ( v1.17.1 )
- Slack API OAuth Bot Token

## Initializing

- devBot is best sbackupsetup to be located in the same directory as your project folder, this allows separation and later support for multiple project setup.

After you have cloned / downloaded devBot and placed it next to your project folder.  We need to cd into the *scripts* folder and execute *init.sh*

```bash
cd scripts
sh init.sh
```

The *init.sh* file will execute a few different things:

- Grant permission to required scripts
- If no bot env
	- download and install required env
- If no config
	- Get name for slack admin and home channel
	- Bot's required OAuth Access Token
	- Get folder name of the project (Should be in same folder as DevBot)
	- Add docker services for the connected project
	- Get path to save backups (command executed)

## Running

After the initializing it setup and you have added your docker services, you simply need to cd into the *scripts* folder again and execute *bot.sh*

```bash
cd scripts
sh bot.sh
```

The *bot.sh* will ask for permission which enables it to launch the docker services with sudo along with enabling it to auto-restart

## Updating

DevBot supports updating it's connected project but only using GitHub.  This also requires the hosting enviroment to have the GitHub credentials saved in some way, otherwise when executing updates you will be required to enter the credentials on the hosting environment.

### DevBot Updates

To update DevBot simply give this command and it will update, and auto-resetart

```bash
@DevBot bot update
```

### Project Updates

```bash
@DevBot server restart -pull
```

## Troubleshooting

### DevBot cannot connect to slack and quits

- Check your *.key.txt* file and ensure it contains only a single line and it matches your Slack Bot OAuth Token

- Try deleting the */bot* folder and run *scripts/init/sh* again
