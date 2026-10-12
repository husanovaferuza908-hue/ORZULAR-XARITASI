"""
Klaviatura va Tugmalar Moduli.
Asosiy ReplyKeyboardMarkup va interaktiv InlineKeyboardMarkup larni taqdim etadi.
"""

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def get_main_reply_keyboard() -> ReplyKeyboardMarkup:
    """Asosiy menyu Reply klaviaturasi."""
    kb = [
        [
            KeyboardButton(text="🎨 Orzular xaritasini yaratish"),
        ],
        [
            KeyboardButton(text="📖 Qanday ishlaydi?"),
            KeyboardButton(text="🖼 Oxirgi yaratgan rasmlarim"),
        ],
        [
            KeyboardButton(text="ℹ️ Bot haqida"),
        ],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def get_cancel_reply_keyboard() -> ReplyKeyboardMarkup:
    """Bekor qilish klaviaturasi."""
    kb = [
        [KeyboardButton(text="❌ Bekor qilish")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def get_result_inline_keyboard(dream_id: int) -> InlineKeyboardMarkup:
    """
    Rasm yaratilgandan keyin uning ostida chiqadigan inline tugmalar:
    - 🔄 Qayta yaratish
    - ✏️ Orzularni o‘zgartirish
    - 📥 Hujjat sifatida yuklab olish
    - 🏠 Bosh menyu
    """
    buttons = [
        [
            InlineKeyboardButton(text="🔄 Qayta yaratish", callback_data=f"regen:{dream_id}"),
            InlineKeyboardButton(text="✏️ Orzularni o‘zgartirish", callback_data=f"edit:{dream_id}"),
        ],
        [
            InlineKeyboardButton(text="📥 Asl sifatda yuklab olish (PNG)", callback_data=f"doc:{dream_id}"),
        ],
        [
            InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_history_item_keyboard(dream_id: int, current_idx: int, total_count: int) -> InlineKeyboardMarkup:
    """Tarixdagi har bir rasm uchun navigatsiya tugmalari."""
    nav_row = []
    if current_idx > 0:
        nav_row.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"hist_page:{current_idx - 1}"))
    nav_row.append(InlineKeyboardButton(text=f"{current_idx + 1}/{total_count}", callback_data="noop"))
    if current_idx < total_count - 1:
        nav_row.append(InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"hist_page:{current_idx + 1}"))

    buttons = [
        nav_row,
        [
            InlineKeyboardButton(text="📥 Asl sifatda yuklash", callback_data=f"doc:{dream_id}"),
            InlineKeyboardButton(text="🔄 Shu orzuni qayta chizish", callback_data=f"regen:{dream_id}"),
        ],
        [
            InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
