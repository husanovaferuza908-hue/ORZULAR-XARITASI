"""
Konfiguratsiya moduli.
Muhit o'zgaruvchilarini (.env) xavfsiz yuklaydi va bot sozlamalarini boshqaradi.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Loyiha ildiz yo'li
BASE_DIR = Path(__file__).resolve().parent

# .env faylini qidirish va yuklash (joriy jildda yoki ota jildda)
env_path = BASE_DIR / ".env"
if not env_path.exists():
    env_path = BASE_DIR.parent / ".env"

load_dotenv(dotenv_path=env_path)


class Config:
    """Botning asosiy konfiguratsiya parametrlari."""
    
    # Telegram Bot
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "").strip()
    
    # OpenAI API
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "").strip()
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip()
    OPENAI_MODEL_TEXT: str = os.getenv("OPENAI_MODEL_TEXT", "gpt-4o-mini").strip()
    OPENAI_MODEL_IMAGE: str = os.getenv("OPENAI_MODEL_IMAGE", "dall-e-3").strip()
    
    # Tasvir parametrlari
    # DALL-E 3 qo'llab-quvvatlaydigan o'lchamlar: '1024x1024', '1792x1024' (landshaft 16:9 ga yaqin), '1024x1792'
    DEFAULT_IMAGE_SIZE: str = os.getenv("DEFAULT_IMAGE_SIZE", "1792x1024").strip()
    DEFAULT_IMAGE_QUALITY: str = os.getenv("DEFAULT_IMAGE_QUALITY", "standard").strip()
    
    # Ma'lumotlar bazasi
    DATABASE_PATH: str = str(BASE_DIR / os.getenv("DATABASE_PATH", "dream_board.db").strip())
    
    # Log darajasi
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").strip().upper()
    
    # Xavfsizlik va cheklovlar
    MIN_DREAM_TEXT_LENGTH: int = 10
    MAX_DREAM_TEXT_LENGTH: int = 1500
    
    @classmethod
    def validate(cls) -> list[str]:
        """Konfiguratsiyani tekshiradi va yetishmayotgan muhim kalitlar ro'yxatini qaytaradi."""
        errors = []
        if not cls.BOT_TOKEN or cls.BOT_TOKEN == "your_telegram_bot_token_here":
            errors.append("BOT_TOKEN ko'rsatilmagan! Iltimos, .env faylida Telegram bot tokeningizni kiriting.")
        return errors

    @classmethod
    def has_openai_key(cls) -> bool:
        """OpenAI kaliti mavjudligini tekshiradi."""
        return bool(cls.OPENAI_API_KEY and cls.OPENAI_API_KEY != "your_openai_api_key_here")


config = Config()
