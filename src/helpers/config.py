import os
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):

    APP_NAME: str
    APP_VERSION: str
    OPENAI_API_KEY: str
    FILE_ALLOWED_EXTENSIONS: list
    MAX_FILE_SIZE_MB: int
    DEFAULT_FILE_CHUNK_SIZE: int

    MONGODB_URL: str
    MONGODB_DATABASE: str

    class Config:
        # check the file exist test before running
        envfile = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
        print("Using envfile at:", envfile)


def get_settings():
    return Settings()