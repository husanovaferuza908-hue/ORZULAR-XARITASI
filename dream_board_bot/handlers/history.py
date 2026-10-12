"""
Boshqaruvchi: Foydalanuvchi yaratgan orzular xaritalari tarixi.
Oxirgi rasmlarni ko'rish, sahifalash va qayta yuklash imkoniyatini beradi.
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile

from database import db
from services import ai_service, image_service
from keyboards import get_history_item_keyboard, get_main_reply_keyboard

logger = logging.getLogger(__name__)

router = Router(name="history_router")


@router.message(F.text == "🖼 Oxirgi yaratgan rasmlarim")
async def show_history_first_page(message: Message):
    """Tarixning birinchi (oxirgi yaratilgan) rasmini ko'rsatish."""
    user_id = message.from_user.id if message.from_user else 0
    total_count = await db.count_user_dreams(user_id)

    if total_count == 0:
        await message.answer(
            "🖼 <b>Siz hali orzular xaritasi yaratmadingiz.</b>\n\n"
            "Ilk orzular xaritangizni yaratish uchun pastdagi "
            "«🎨 Orzular xaritasini yaratish» tugmasini bosing!",
            parse_mode="HTML",
            reply_markup=get_main_reply_keyboard(),
        )
        return

    await _render_history_item(message, user_id, index=0, total_count=total_count)


@router.callback_query(F.data.startswith("hist_page:"))
async def handle_history_pagination(callback: CallbackQuery):
    """Tarix sahifalari bo'ylab o'tish."""
    page_str = callback.data.split(":")[1]
    if not page_str.isdigit():
        await callback.answer()
        return

    target_idx = int(page_str)
    user_id = callback.from_user.id
    total_count = await db.count_user_dreams(user_id)

    if target_idx < 0 or target_idx >= total_count:
        await callback.answer("Sahifa mavjud emas", show_alert=True)
        return

    await callback.answer()
    if callback.message:
        await _render_history_item(callback.message, user_id, index=target_idx, total_count=total_count)


async def _render_history_item(target_message: Message, user_id: int, index: int, total_count: int):
    """Tarixdagi bitta elementni yuboradi."""
    items = await db.get_user_history(user_id, limit=1, offset=index)
    if not items:
        await target_message.answer("Ma'lumot topilmadi.")
        return

    item = items[0]
    dream_id = item["id"]
    date_str = item["created_at"]
    orig_text = item["original_text"]
    categories = item.get("categorized", {})
    file_id = item.get("file_id")

    caption = (
        f"🖼 <b>Orzular xaritasi #{dream_id}</b> ({index + 1}/{total_count})\n"
        f"📅 <i>Yaratilgan vaqti:</i> {date_str}\n\n"
        f"📝 <b>Orzularingiz:</b>\n<i>«{orig_text[:250]}{'...' if len(orig_text) > 250 else ''}»</i>"
    )

    kb = get_history_item_keyboard(dream_id, current_idx=index, total_count=total_count)

    # Agar Telegram file_id mavjud bo'lsa darhol yuboramiz
    if file_id:
        try:
            await target_message.answer_photo(
                photo=file_id,
                caption=caption,
                parse_mode="HTML",
                reply_markup=kb,
            )
            return
        except Exception as e:
            logger.warning(f"file_id orqali yuborishda xatolik: {e}")

    # Agar file_id ishlamasa, image_url yoki qayta generatsiya
    image_bytes = None
    if item.get("image_url"):
        image_bytes = await image_service.download_image_bytes(item["image_url"])

    if not image_bytes:
        image_bytes = image_service._generate_demo_board_image(orig_text, categories)

    input_file = BufferedInputFile(image_bytes, filename=f"vision_board_{dream_id}.jpg")
    await target_message.answer_photo(
        photo=input_file,
        caption=caption,
        parse_mode="HTML",
        reply_markup=kb,
    )
