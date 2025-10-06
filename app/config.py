import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "chatbot_data")

settings = Settings()