import os

from dotenv import load_dotenv

load_dotenv()

USERNAME_AS_EMAIL = os.environ["USERNAME_AS_EMAIL"]
PASSWORD = os.environ["PASSWORD"]
URL = os.environ["URL"]

APP_NAME = "mars"
CLIENT_FILE = "pytooter_clientcred.secret"
