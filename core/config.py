import os
from dotenv import load_dotenv

load_dotenv(override=True)

class Config:
    def __init__(self):
        self.MYSQL_USERNAME = os.getenv('MYSQL_USERNAME')
        self.MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
        self.MYSQL_HOST = os.getenv('MYSQL_HOST')
        self.MYSQL_PORT = os.getenv('MYSQL_PORT')
        self.MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
        self.ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')

        self.AWS_CHATGPT_API_URL = os.getenv('AWS_CHATGPT_API_URL')
        self.AWS_CHATGPT_API_KEY = os.getenv('AWS_CHATGPT_API_KEY')

        self.WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')

        self.DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

        self.DEBUG = os.getenv('DEBUG', 'FALSE') == 'TRUE'

config = Config()