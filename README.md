# QueueUp Discord Bot
Basically QueueUp Live But on Discord

## Running it Locally
You would need to create environment variables in order for the program to work. 
You need to create a .env file inside your project directory, and assign these variable names. 
```
TOKEN=[Token from Discord API]
QUEUE_CHANNEL_ID=[Text Channel ID to run the queue in]
HISTORY_CHANNEL_ID=[Text Channel ID to store history]
UTA_ROLE_ID=[Role ID for the UTAs]
GTA_ROLE_ID=[Role ID for the GTAs]
PROFESSOR_ROLE_ID=[Role ID for Professor] 
WAITING_ROOM=[Voice Channel ID for Waiting Room]
BOT_CHANNEL_ID=[Text Channel ID for bot commands only for TAs]
ROOMS="{'voice channel': 'text channel'}"
DATABASE=[Location of the Database]
```
For rooms, each voice channel will be assigned a text channel. As a result, if there is a video failure, the TA and student can still connect via text channel.

You can store the environment variables inside a .env file. In production, it doesn't use load_dotenv, so do not create .env for production. 

To run it, you can run bin/gueueup-bot directly. 
```bash
python3 bin/queueup-bot
```
Please note that your working directory must be the root of the file so it can access the .env file. I would recommend using Pycharm for this project. 

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

## Installation [Production]
You can install it using the following command
```bash
python3 setup.py install --user
```

You run it using the following
```bash
queueup-bot
```

## Basic setup [Production]
```.
Home Directory
│
├─── environments 
│    └── queueup.environment [Location to store enivronment variables]
│
├─── scripts 
│    └── queueup.sh [Used only for CI/CD. It is optional]
```

## Running on AWS EC2 Instance
There is a script called ec2.sh, which can be runned on an EC2 instance if you decide to run the bot on an EC2 Instance. The Bot is currently being runned by the cheapest EC2 Instance on AWS. 

