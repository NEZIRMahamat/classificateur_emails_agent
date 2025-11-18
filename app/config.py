# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()   # ← charge le .env dans TOUS les processus

class Settings:
    groq_api_key = os.getenv("GROQ_API_KEY")
    gmail_user = os.getenv("GMAIL_USER")

settings = Settings()
