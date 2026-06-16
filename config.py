import os
from dotenv import load_dotenv

class Config:
    load_dotenv()
    TG_TOKEN = os.getenv("TG_TOKEN")
    FAST_API_HOST = os.getenv("FAST_API_HOST")
    FAST_API_PORT = int(os.getenv("FAST_API_PORT"))
    MODEL_PATH = os.getenv("MODEL_PATH")

    @classmethod
    def validate(cls):
        if not cls.TG_TOKEN:
            raise ValueError("Ошибка: Не задан TG_TOKEN в файле .env")
        if not cls.MODEL_PATH:
            raise ValueError("Ошибка: Не задан MODEL_PATH в файле .env")