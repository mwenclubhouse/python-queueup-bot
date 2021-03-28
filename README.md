# QueueUp Discord Bot
Basically QueueUp Live But on Discord

## Running it Locally
You would need to create environment variables in order for the program to work. 
```bash
TOKEN=[Token from Discord API]
QUEUE_CHANNEL_ID=[Text Channel ID to run the queue in]
HISTORY_CHANNEL_ID=[Text Channel ID to store history]
UTA_ROLE_ID=[Role ID for the UTAs]
GTA_ROLE_ID=[Role ID for the GTAs]
PROFESSOR_ROLE_ID=[Role ID for Professor] 
```
You can store the environment variables inside a .env file. In production, it doesn't use load_dotenv, so do not create .env for production. 

To run it, you can run bin/gueueup-bot directly. 
```bash
python3 bin/queueup-bot
```

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

