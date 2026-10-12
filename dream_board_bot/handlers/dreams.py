"""
Boshqaruvchi: Orzularni qabul qilish, tahlil qilish, generatsiya va tahrirlash.
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ChatAction

from config import config
from database import db
from services import ai_service, image_service
from keyboards import (
    get_main_reply_keyboard,
    get_cancel_reply_keyboard,
    get_result_inline_keyboard,
)

logger = logging.getLogger(__name__)

router = Router(name="dreams_router")


class DreamStates(StatesGroup):
    """Orzular yaratish va tahrirlash holatlari."""
    waiting_for_text = State()
    waiting_for_edit = State()


DREAM_PROMPT_INSTRUCTION = (
    "✨ <b>Kelajakda nimalarga erishmoqchisiz?</b>\n\n"
    "Orzularingizni erkin va iloji boricha batafsil yozing.\n\n"
    "💡 <i>Misol:</i>\n"
    "«Men kuchli dasturchi bo‘lishni, zamonaviy shinam uy sotib olishni, "
    "yangi avtomobil olishni va dunyo bo‘ylab sayohat qilishni xohlayman.»\n\n"
    "👇 <b>Orzularingizni quyida yozib yuboring:</b>"
)


@router.message(F.text == "🎨 Orzular xaritasini yaratish")
async def start_dream_creation(message: Message, state: FSMContext):
    """Orzu kiritish jarayonini boshlash."""
    await state.set_state(DreamStates.waiting_for_text)
    await message.answer(
        DREAM_PROMPT_INSTRUCTION,
        reply_markup=get_cancel_reply_keyboard(),
        parse_mode="HTML",
    )


@router.message(DreamStates.waiting_for_text)
@router.message(DreamStates.waiting_for_edit)
async def process_dream_input(message: Message, state: FSMContext):
    """Foydalanuvchi yozgan orzular matnini qabul qilish va generatsiya qilish."""
    text = (message.text or "").strip()

    # Bekor qilish tugmasi bosilgan bo'lsa
    if text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_main_reply_keyboard())
        return

    # Validatsiya
    if len(text) < config.MIN_DREAM_TEXT_LENGTH:
        await message.answer(
            f"⚠️ Matn juda qisqa ({len(text)} ta belgi). "
            f"Iltimos, orzularingizni biroz batafsilroq yozing (kamida {config.MIN_DREAM_TEXT_LENGTH} ta belgi).",
            reply_markup=get_cancel_reply_keyboard(),
        )
        return

    if len(text) > config.MAX_DREAM_TEXT_LENGTH:
        await message.answer(
            f"⚠️ Matn juda uzun ({len(text)} ta belgi). "
            f"Iltimos, {config.MAX_DREAM_TEXT_LENGTH} ta belgidan oshirmang.",
            reply_markup=get_cancel_reply_keyboard(),
        )
        return

    user_id = message.from_user.id if message.from_user else 0
    await state.clear()

    # Generatsiya jarayoni
    await _execute_generation(message, user_id, text)


async def _execute_generation(message: Message, user_id: int, text: str):
    """Orzularni tahlil qilish, rasm chizish va foydalanuvchiga taqdim etish."""
    # 1. Tahlil status xabari
    status_msg = await message.answer(
        "⏳ <b>Orzularingiz tahlil qilinmoqda...</b>\n<i>(Mavzular va vizual prompt aniqlanmoqda)</i>",
        parse_mode="HTML",
    )
    
    # Typing / Action yuborish
    if message.bot:
        await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.UPLOAD_PHOTO)

    # Matnni tahlil qilish
    analysis = await ai_service.analyze_and_build_prompt(text)
    categories = analysis.get("categories", {})
    motivation = analysis.get("motivation", "")
    dalle_prompt = analysis.get("dalle_prompt", "")
    is_ai_text = analysis.get("is_ai_generated", False)

    # 2. Rasm yaratish status xabari
    try:
        await status_msg.edit_text(
            "🎨 <b>Sun'iy intellekt orzular xaritangizni yaratmoqda...</b>\n"
            "<i>(Bu jarayon 15-30 soniya vaqt olishi mumkin, iltimos kuting...)</i>",
            parse_mode="HTML",
        )
    except Exception:
        pass

    if message.bot:
        await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.UPLOAD_PHOTO)

    # Rasm generatsiyasi
    image_bytes, image_url, is_real_ai, err_info = await image_service.generate_vision_board(
        prompt=dalle_prompt,
        user_text=text,
        categories=categories,
    )

    if not image_bytes:
        await status_msg.edit_text(
            f"❌ <b>Afsuski, tasvir yaratishda xatolik yuz berdi.</b>\n\n"
            f"Izoh: <i>{err_info or 'Noma\'lum xatolik'}</i>\n\n"
            "Iltimos, qaytadan urinib ko'ring yoki keyinroq sinab ko'ring.",
            parse_mode="HTML",
            reply_markup=get_main_reply_keyboard(),
        )
        return

    # Xulosa matnini shakllantirish
    caption = ai_service.format_analysis_summary(categories, motivation, is_ai=is_ai_text)
    if not is_real_ai:
        caption += (
            "\n\n⚠️ <b>DIQQAT (DEMO REJIM):</b>\n"
            "Serverda <code>OPENAI_API_KEY</code> sozlanmaganligi sababli, yuqoridagi rasm namuna sifatida yaratildi. "
            "Haqiqiy DALL-E 3 sun'iy intellekti yaratgan rasmni olish uchun <code>.env</code> fayliga API kalitingizni kiriting."
        )

    # Agar caption 1024 belgidan oshib ketsa, qisqartirish
    if len(caption) > 1020:
        caption = caption[:1015] + "..."

    # Bazaga saqlash
    dream_id = await db.add_dream(
        user_id=user_id,
        original_text=text,
        categorized_data=categories,
        prompt=dalle_prompt,
        image_url=image_url,
    )

    # Rasmni yuborish
    input_file = BufferedInputFile(image_bytes, filename=f"vision_board_{dream_id}.jpg")
    
    try:
        await status_msg.delete()
    except Exception:
        pass

    sent_msg = await message.answer_photo(
        photo=input_file,
        caption=caption,
        parse_mode="HTML",
        reply_markup=get_result_inline_keyboard(dream_id),
    )

    # Telegram file_id ni bazaga yangilash (tezkor qayta yuklash uchun)
    if sent_msg.photo:
        highest_res_photo = sent_msg.photo[-1]
        await db.update_dream_file_id(dream_id, highest_res_photo.file_id)

    # Bosh menyu klaviaturasini ham ko'rsatib qo'yamiz
    await message.answer(
        "Muvaffaqiyatli yakunlandi! Rasm ostidagi tugmalar orqali uni o'zgartirishingiz yoki qayta yaratishingiz mumkin.",
        reply_markup=get_main_reply_keyboard(),
    )


@router.callback_query(F.data.startswith("regen:"))
async def handle_regenerate(callback: CallbackQuery):
    """Orzular xaritasini yangitdan qayta yaratish."""
    dream_id_str = callback.data.split(":")[1]
    if not dream_id_str.isdigit():
        await callback.answer("Noto'g'ri ID", show_alert=True)
        return

    dream_id = int(dream_id_str)
    dream = await db.get_dream(dream_id)
    if not dream:
        await callback.answer("Ma'lumot topilmadi!", show_alert=True)
        return

    await callback.answer("Qayta yaratish boshlanmoqda...")
    if callback.message:
        user_id = callback.from_user.id
        await _execute_generation(callback.message, user_id, dream["original_text"])


@router.callback_query(F.data.startswith("edit:"))
async def handle_edit_dream(callback: CallbackQuery, state: FSMContext):
    """Mavjud orzularni tahrirlash."""
    dream_id_str = callback.data.split(":")[1]
    if not dream_id_str.isdigit():
        await callback.answer("Noto'g'ri ID", show_alert=True)
        return

    dream_id = int(dream_id_str)
    dream = await db.get_dream(dream_id)
    if not dream:
        await callback.answer("Ma'lumot topilmadi!", show_alert=True)
        return

    await state.set_state(DreamStates.waiting_for_edit)
    await callback.answer()

    if callback.message:
        await callback.message.answer(
            f"✏️ <b>Orzularingizni o'zgartirish</b>\n\n"
            f"Avvalgi matningiz:\n<i>«{dream['original_text']}»</i>\n\n"
            f"Iltimos, yangi yoki to'ldirilgan variantini yozib yuboring:",
            parse_mode="HTML",
            reply_markup=get_cancel_reply_keyboard(),
        )


@router.callback_query(F.data.startswith("doc:"))
async def handle_download_document(callback: CallbackQuery):
    """Rasmni fayl (hujjat) ko'rinishida jo'natish."""
    dream_id_str = callback.data.split(":")[1]
    if not dream_id_str.isdigit():
        await callback.answer("Noto'g'ri ID", show_alert=True)
        return

    dream_id = int(dream_id_str)
    dream = await db.get_dream(dream_id)
    if not dream:
        await callback.answer("Ma'lumot topilmadi!", show_alert=True)
        return

    await callback.answer("Fayl tayyorlanmoqda...")

    # Agar image_url mavjud bo'lsa yuklab olamiz
    doc_bytes = None
    if dream.get("image_url"):
        doc_bytes = await image_service.download_image_bytes(dream["image_url"])

    # Agar yo'q bo'lsa demo generatordan olamiz
    if not doc_bytes:
        doc_bytes = image_service._generate_demo_board_image(
            dream["original_text"],
            dream.get("categorized", {}),
        )

    doc_file = BufferedInputFile(doc_bytes, filename=f"Vision_Board_{dream_id}.jpg")
    if callback.message:
        await callback.message.answer_document(
            document=doc_file,
            caption=f"📁 <b>Orzular xaritasi #{dream_id}</b>\nAsl sifatda saqlab oling!",
            parse_mode="HTML",
        )
