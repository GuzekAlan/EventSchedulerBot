# EventSchedulerBot
Discord bot with slash commands to schedule events

## Requirements:
* Discord bot `TOKEN` key found in: https://discord.com/developers/applications
* Python > 3.10 installed
* Docker installed

## Installation:
* Create `.env` file with discord bot `TOKEN`
* run `$ docker compose up -d`
* If docker deamon does not work try `$ sudo dockerd &`

## Usage:
* To use this bot you need to invite it to your server
* Set channel for discord bot to send messages by typing `!set-channel` in desired channel
* To start scheduling open channel in discord and type `/` to see all available commands
* After selecting command there will be hints on how to use it
