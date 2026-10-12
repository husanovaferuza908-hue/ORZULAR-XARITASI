"""
Orzular Xaritasi AI Bot - Testlar to'plami.
DB, AIService va ImageService larning to'g'ri ishlashini tekshiradi.
"""

import asyncio
import os
import sys
from pathlib import Path

# Windows konsolida UTF-8 va emojilar xatosiz chiqishi uchun
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# dream_board_bot yo'lini sys.path ga qo'shish
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from database import db
from services import ai_service, image_service
from config import config


async def run_tests():
    print("========================================")
    print("🧪 Testlar ishga tushirilmoqda...")
    print("========================================")

    # 1. Ma'lumotlar bazasi testi
    print("\n[1/3] Ma'lumotlar bazasi (SQLite) testi...")
    test_db_path = PROJECT_DIR / "test_dream_board.db"
    db.db_path = str(test_db_path)
    
    await db.init_db()
    print("  ✓ DB initsializatsiya qilindi.")

    await db.upsert_user(12345, "testuser", "Test Foydalanuvchi")
    print("  ✓ Foydalanuvchi qo'shildi.")

    test_dream_id = await db.add_dream(
        user_id=12345,
        original_text="Men kuchli dasturchi bo'lishni va Dubayga sayohat qilishni xohlayman.",
        categorized_data={"career": "Dasturchi bo'lish", "travel": "Dubayga sayohat"},
        prompt="A high quality vision board showing coding setup and Dubai skyline",
        image_url="http://example.com/test.jpg",
    )
    print(f"  ✓ Orzu saqlandi, ID: {test_dream_id}")

    history = await db.get_user_history(12345)
    assert len(history) == 1, "Tarixda bitta yozuv bo'lishi kerak!"
    assert history[0]["id"] == test_dream_id
    print("  ✓ Foydalanuvchi tarixi to'g'ri olindi.")

    count = await db.count_user_dreams(12345)
    assert count == 1
    print("  ✓ Jami orzular soni to'g'ri hisoblandi.")

    # 2. AI Servis tahlil testi (Offline / Heuristic)
    print("\n[2/3] AI Matn Tahlili testi...")
    user_text = "Men IT kompaniyada Senior dasturchi bo'lishni, yangi BMW xarid qilishni va oilam bilan tog'da dam olishni istayman."
    result = await ai_service.analyze_and_build_prompt(user_text)
    
    print(f"  ✓ Tahlil qilindi: {list(result['categories'].keys())}")
    print(f"  ✓ Prompt: {result['dalle_prompt'][:100]}...")
    assert len(result["categories"]) > 0, "Kamida bitta toifa aniqlanishi kerak!"
    assert "dalle_prompt" in result
    
    summary = ai_service.format_analysis_summary(result["categories"], result["motivation"], is_ai=result["is_ai_generated"])
    print(f"  ✓ Formatlangan matn uzunligi: {len(summary)} belgi.")

    # 3. Tasvir generatsiyasi testi (Demo Image Generator)
    print("\n[3/3] Tasvir generatsiyasi (Demo generator) testi...")
    img_bytes, img_url, is_real, err = await image_service.generate_vision_board(
        prompt=result["dalle_prompt"],
        user_text=user_text,
        categories=result["categories"],
    )
    assert img_bytes is not None, "Tasvir baytlari yaratilishi shart!"
    assert len(img_bytes) > 1000, "Tasvir hajmi 1KB dan katta bo'lishi kerak!"
    print(f"  ✓ Tasvir muvaffaqiyatli tayyorlandi! Hajmi: {len(img_bytes)} bayt. (Demo: {not is_real})")

    # Tozalash
    if test_db_path.exists():
        try:
            os.remove(test_db_path)
        except Exception:
            pass

    print("\n========================================")
    print("🎉 BARCHA TESTLAR MUVAFFAQIYATLI O'TDI!")
    print("========================================")


if __name__ == "__main__":
    asyncio.run(run_tests())
