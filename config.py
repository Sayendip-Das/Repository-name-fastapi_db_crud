import os
from dotenv import load_dotenv

class Settings:
    origin = os.getenv("origin")
    SECRET_KEY = os.getenv("SECRET_KEY")

setting = Settings()