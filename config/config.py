import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
TOPIC_NAME = os.getenv('TOPIC_NAME')