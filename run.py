"""
Ildizdan botni tezkor ishga tushirish skripti.
"""
import sys
from pathlib import Path

# dream_board_bot papkasini sys.path ga qo'shish
BASE_DIR = Path(__file__).resolve().parent / "dream_board_bot"
sys.path.insert(0, str(BASE_DIR))

if __name__ == "__main__":
    from bot import main
    import asyncio
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
