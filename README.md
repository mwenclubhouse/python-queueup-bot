# Python QueueUp Discord Bot
Basically QueueUp Live But on Discord. 

## Updates to Python Program
We killed the project for a potential NodeJS Alternative. However, that would of been more work than 
to salvage what is currently written in Python. Therefore, this Python Program will live, and it will 
be connected to https://www.mwenclubhouse.com/queueup very soon. At the meantime, this will continued
to be in development until the website version of the website is up and running.

## Creating an Account and Giving Suggestions
To create an account, please contact mattwen2018@gmail.com to try out the server. To keep in 
compliance with FERPA, we will also be releasing a docker container of this program to run 
on your school server soon (you will also need a free tier Google Firebase Account as well). However, you are more than welcome to use the website, which will be released soon.

## New Features 
1. Google Document Support will be added into the project at scale.
2. Commands inside the voice channel to clear any existing text for the TA
3. Website with Zoom Support if user doesn't want to install discord
4. Website to control bot

## Permissions to Set for the bot
1. Move Members
2. Read Message History
3. Manage Messages
4. Add Reactions
5. Embed Links
6. Send Messages
7. Manage Emojis
8. Manage Channels
9. View Channels
10. Manage Roles

Also enable Privileged Gateway Intents.
- This gives the bot more control over getting members inside a server.

## Basic setup [Production] (Changing to Docker Container -> Work in Progress)
```.
Home Directory
│
├─── bucket 
│    └── queueup.db [database for Server]
│    └── example-server-id.db [server's attributes (rooms, queues, history, etc)]
│
└─── environments 
     └── queueup.environment [Location to store enivronment variables]
```