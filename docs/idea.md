# Idea for an applicaiton

## Process of setting up discrod bot on channel
1. Add discord bot from link
2. Set up users to add to scheduling (all users available)

## How to add event
1. Use slash command to add event
2. Modal pops up and lets you insert info
3. Choose which termins are available (hours, days)
4. Bot sends every user messages to pich up dates:
    * bot sends multiple messages to one user on which user can add emoji `great`/`ok`/`no`
    * it allows to set whole day to one of this options
    * last message is a button to confirm which will delete previous messages
5. After all users submit answer `accept`/`decline` event

## Interactions with planned Event
1. Creator:
    * cancel event
    * edit information
    * request date change (process of choosing date)
    * add user
2. Participant:
    * set reminder for event

