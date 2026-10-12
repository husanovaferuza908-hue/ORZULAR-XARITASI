"""
Orzular Xaritasi AI - Asosiy Telegram Bot Dasturi.
Aiogram 3 asosida yaratilgan, to'liq asinxron bot.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Windows konsolida UTF-8 va emojilar xatosiz chiqishi uchun
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# Joriy jildni sys.path ga qo'shish
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from config import config
from database import db
from handlers import main_router

# Logging sozlamalari (Konsol va bot.log fayli)
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(CURRENT_DIR / "bot.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("dream_board_bot")


def print_banner():
    """Bot ishga tushganda konsolga chiroyli ma'lumot chiqaradi."""
    banner = f"""
============================================================
       🌟 ORZULAR XARITASI AI — VISION BOARD BOT 🌟        
============================================================
 Python:         {sys.version.split()[0]}
 Ma'lumotlar bazasi: {config.DATABASE_PATH}
 Tasvir modeli:  {config.OPENAI_MODEL_IMAGE} ({config.DEFAULT_IMAGE_SIZE})
 Matn modeli:    {config.OPENAI_MODEL_TEXT}
 OpenAI Kaliti:  {'✅ O\'rnatilgan' if config.has_openai_key() else '⚠️ O\'rnatilmagan (Demo rejim)'}
============================================================
"""
    print(banner)


async def main():
    """Botni ishga tushirish funksiyasi."""
    print_banner()

    # Konfiguratsiyani tekshirish
    validation_errors = config.validate()
    if validation_errors:
        print("\n❌ QAT'IY XATOLIK:")
        for err in validation_errors:
            print(f"  • {err}")
        print("\n💡 QANDAY TUZATISH MUMKIN:")
        print("  1. 'dream_board_bot/.env.example' faylidan nusxa olib, '.env' nomli fayl yarating.")
        print("  2. @BotFather dan olgan bot tokeningizni BOT_TOKEN ga qo'ying.")
        print("  3. OpenAI API kalitingizni OPENAI_API_KEY ga qo'ying.")
        print("  4. Dasturni qaytadan ishga tushiring: python bot.py\n")
        return

    # Ma'lumotlar bazasini initsializatsiya qilish
    try:
        await db.init_db()
    except Exception as e:
        logger.critical(f"Ma'lumotlar bazasini ishga tushirishda xatolik: {e}")
        return

    # Bot va Dispatcher yaratish
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Routerlarni ro'yxatdan o'tkazish
    dp.include_router(main_router)

    # Eski xabarlarni tozalash va bot haqida ma'lumot olish
    try:
        bot_info = await bot.get_me()
        logger.info(f"Bot muvaffaqiyatli ulandi: @{bot_info.username} (ID: {bot_info.id})")
        print(f"🚀 Bot ishga tushdi: https://t.me/{bot_info.username}")
    except Exception as e:
        logger.error(f"Telegram API bilan bog'lanishda xatolik: {e}")
        print(f"❌ Telegram API bilan bog'lanishda xatolik. Bot tokenini tekshiring: {e}")
        await bot.session.close()
        return

    await bot.delete_webhook(drop_pending_updates=True)

    # Pollingni boshlash
    try:
        logger.info("Bot polling rejimi boshlandi...")
        await dp.start_polling(bot)
    finally:
        logger.info("Bot to'xtatilmoqda...")
        await bot.session.close()
        logger.info("Bot to'xtatildi.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot foydalanuvchi tomonidan to'xtatildi.")
