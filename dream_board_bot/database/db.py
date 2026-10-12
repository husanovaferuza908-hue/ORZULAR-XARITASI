"""
SQLite ma'lumotlar bazasi moduli.
Foydalanuvchilar va orzular xaritasi generatsiyalari tarixini asinxron boshqaradi.
"""

import json
import logging
from typing import Optional, Any
import aiosqlite

from config import config

logger = logging.getLogger(__name__)


class Database:
    """Asinxron SQLite ma'lumotlar bazasi boshqaruvchisi."""

    def __init__(self, db_path: str = config.DATABASE_PATH):
        self.db_path = db_path

    async def init_db(self) -> None:
        """Ma'lumotlar bazasi jadvallarini yaratadi."""
        logger.info(f"Ma'lumotlar bazasi ishga tushirilmoqda: {self.db_path}")
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("PRAGMA journal_mode=WAL;")
            await db.execute("PRAGMA foreign_keys=ON;")
            
            # Foydalanuvchilar jadvali
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Orzular xaritalari jadvali
            await db.execute("""
                CREATE TABLE IF NOT EXISTS dreams (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    original_text TEXT NOT NULL,
                    categorized_json TEXT,
                    prompt TEXT NOT NULL,
                    image_url TEXT,
                    file_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
                );
            """)

            # Tezkor qidiruv uchun indeks
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_dreams_user_id ON dreams(user_id);
            """)

            await db.commit()
            logger.info("Ma'lumotlar bazasi jadvallari muvaffaqiyatli tekshirildi.")

    async def upsert_user(self, user_id: int, username: Optional[str], first_name: Optional[str]) -> None:
        """Foydalanuvchini qo'shadi yoki uning oxirgi faolligini yangilaydi."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO users (user_id, username, first_name, last_active)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    username = excluded.username,
                    first_name = excluded.first_name,
                    last_active = CURRENT_TIMESTAMP;
            """, (user_id, username, first_name))
            await db.commit()

    async def add_dream(
        self,
        user_id: int,
        original_text: str,
        categorized_data: dict[str, Any],
        prompt: str,
        image_url: Optional[str] = None,
        file_id: Optional[str] = None,
    ) -> int:
        """Yangi yaratilgan orzular xaritasini saqlaydi va uning ID sini qaytaradi."""
        categorized_json = json.dumps(categorized_data, ensure_ascii=False)
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO dreams (user_id, original_text, categorized_json, prompt, image_url, file_id)
                VALUES (?, ?, ?, ?, ?, ?);
            """, (user_id, original_text, categorized_json, prompt, image_url, file_id))
            await db.commit()
            return cursor.lastrowid or 0

    async def update_dream_file_id(self, dream_id: int, file_id: str) -> None:
        """Yuborilgan rasmning Telegram file_id sini saqlaydi."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE dreams SET file_id = ? WHERE id = ?;
            """, (file_id, dream_id))
            await db.commit()

    async def get_dream(self, dream_id: int) -> Optional[dict[str, Any]]:
        """Aynan bitta orzular xaritasini ID bo'yicha oladi."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT id, user_id, original_text, categorized_json, prompt, image_url, file_id, created_at
                FROM dreams WHERE id = ?;
            """, (dream_id,))
            row = await cursor.fetchone()
            if not row:
                return None
            return {
                "id": row["id"],
                "user_id": row["user_id"],
                "original_text": row["original_text"],
                "categorized": json.loads(row["categorized_json"]) if row["categorized_json"] else {},
                "prompt": row["prompt"],
                "image_url": row["image_url"],
                "file_id": row["file_id"],
                "created_at": row["created_at"],
            }

    async def get_user_history(self, user_id: int, limit: int = 5, offset: int = 0) -> list[dict[str, Any]]:
        """Foydalanuvchining oxirgi yaratilgan orzular xaritalari ro'yxatini qaytaradi."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT id, user_id, original_text, categorized_json, prompt, image_url, file_id, created_at
                FROM dreams
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?;
            """, (user_id, limit, offset))
            rows = await cursor.fetchall()
            
            history = []
            for row in rows:
                history.append({
                    "id": row["id"],
                    "user_id": row["user_id"],
                    "original_text": row["original_text"],
                    "categorized": json.loads(row["categorized_json"]) if row["categorized_json"] else {},
                    "prompt": row["prompt"],
                    "image_url": row["image_url"],
                    "file_id": row["file_id"],
                    "created_at": row["created_at"],
                })
            return history

    async def count_user_dreams(self, user_id: int) -> int:
        """Foydalanuvchi jami nechta xarita yaratganligini hisoblaydi."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT COUNT(*) FROM dreams WHERE user_id = ?;
            """, (user_id,))
            row = await cursor.fetchone()
            return row[0] if row else 0


db = Database()
