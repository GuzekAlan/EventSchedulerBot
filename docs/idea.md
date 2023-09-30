# How to use

## What is it?
Bot for scheduling events. It allows to pick the best date for all participants. It also takes into consideration the time of the event and other events planned by participants.

## How to schedule an event?
1. Use slash command `/schedule-event`
2. Message with embed is sent to the channel
3. Using buttons fill the information needed (Schedule Event Message)
4. After all information is filled click `Schedule` button
5. Bot sends message with information about event and buttons to add participants
6. Participants choose times when they are available (Select Dates Message)
5. After all users submit answer bot sends message to the creator to accept (Accept Event Message)
6. Bot creates discord event and saves it in database

# UI

## Schedule Event Message
Message with embed which shows informations:
* title
* description
* dateframe (from when to when)
* participants (if there are many the list is truncated)
There are buttons which allow to add/edit informations:
1. `Add participant` - adds one user or many (via `role`) to the event (using discord select)
2. `Remove participant` - removes one user or many (via `role`) from the event (using discord select)
3. `Add Informations`/`Edit Informations` - allows to add informations (or edit if some informations are already added) about event by discord modal: 
    * title
    * description
    * tags
    * dateframe (from when to when)
4. `Schedule` - sends message to the channel with information about event and buttons to add participants. It is disabled before every required information is filled.

## Select Dates Message
Message with informations:
* title
* date

Buttons:
1. `Previous day` - changes date to previous day
2. `Previous week` - changes date to previous week
2. `Next day` - changes date to next day
3. `Next week` - changes date to next week
4. `Submit` - approves selected dates and stores it in database

Select fields (multiple select of hours when user is available):
1. `GREEN` - user is available and wants event to be at this time 
2. `YELLOW` - user is available but prefers other time
3. `RED` - user is not available at this time

## Accept Event Message
Message with embed showing time selected and two buttons:
1. `Accept` - creates discord event and saves it in database
2. `Decline` - deletes event from database

# FAQ

### Can you change time or date of event?
Yes you can but then the whole process of selecting date starts again.

### Can you add user to already created event?
Yes, users can be added later but they cannot choose best date for them and must accept already selected date


# Other

## Interactions with planned Event
1. Creator:
    * cancel event
    * edit information
    * request date change (process of choosing date)
    * add user
2. Participant:
    * set reminder for event