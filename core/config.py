import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self.MYSQL_USERNAME = os.getenv('MYSQL_USERNAME')
        self.MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
        self.MYSQL_HOST = os.getenv('MYSQL_HOST')
        self.MYSQL_PORT = os.getenv('MYSQL_PORT')
        self.MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
        self.ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')

        self.AWS_CHATGPT_API_URL = os.getenv('AWS_CHATGPT_API_URL')

config = Config()