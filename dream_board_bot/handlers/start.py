"""
Boshqaruvchi: Start va umumiy ma'lumotlar.
/start, /help, qo'llanma va bot haqidagi ma'lumotlarni qayta ishlaydi.
"""

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database import db
from keyboards import get_main_reply_keyboard

router = Router(name="start_router")


WELCOME_TEXT = (
    "🌟 <b>Assalomu alaykum! Orzular Xaritasi AI botiga xush kelibsiz!</b>\n\n"
    "Orzularingizni yozing. Men ularni professional va motivatsion rasmga aylantiraman.\n\n"
    "✨ <i>«Kelajagingni tasavvur qil. Orzularingni yoz. AI esa ularni ilhomlantiruvchi orzular xaritasiga aylantirsin.»</i>\n\n"
    "Quyidagi tugmalardan birini tanlang:"
)

HOW_IT_WORKS_TEXT = (
    "📖 <b>Orzular xaritasi qanday ishlaydi?</b>\n\n"
    "1️⃣ <b>Orzularingizni yozasiz:</b>\n"
    "Kelajakda nimalarga erishmoqchi ekanligingizni erkin matn shaklida yuborasiz.\n\n"
    "2️⃣ <b>Sun'iy intellekt tahlil qiladi:</b>\n"
    "AI orzularingizni quyidagi 7 ta muhim yo'nalish bo'yicha ajratadi:\n"
    "   • 🎓 Ta’lim va bilim\n"
    "   • 💼 Kasb va biznes\n"
    "   • 🏡 Uy va avtomobil\n"
    "   • ✈️ Sayohat va kashfiyot\n"
    "   • 🌟 Shaxsiy rivojlanish\n"
    "   • 🏃 Sport va sog‘lom turmush\n"
    "   • 👨‍👩‍👧 Oila va hayot tarzi\n\n"
    "3️⃣ <b>Kollaj yaratiladi:</b>\n"
    "AI har bir maqsadingizni o'zida aks ettirgan, kinematik yorug'likka ega, keraksiz yozuvlarsiz yagona estetik kollaj (Vision Board) chizadi.\n\n"
    "4️⃣ <b>Saqlash va qayta yaratish:</b>\n"
    "Rasmni telefoningizga yuklab olishingiz, fon rasmiga qo'yishingiz yoki yangi variantlarni qayta yaratishingiz mumkin!"
)

ABOUT_BOT_TEXT = (
    "ℹ️ <b>Orzular Xaritasi AI (Vision Board Bot)</b>\n\n"
    "Ushbu bot insonlarga o'z orzu va maqsadlarini aniq tasavvur qilishga va "
    "vizual motivatsiya olishga yordam berish uchun yaratilgan.\n\n"
    "🛠 <b>Texnologiyalar:</b>\n"
    "• Dasturlash tili: Python 3.11+\n"
    "• Bot kutubxonasi: aiogram 3 (Asinxron)\n"
    "• Tasvir AI: OpenAI DALL-E 3\n"
    "• Matn tahlili: OpenAI GPT-4o-mini\n"
    "• Ma'lumotlar bazasi: SQLite (aiosqlite)\n\n"
    "⚡️ <i>Har kuni o'z orzularingizni ko'rib turing va ularga erishing!</i>"
)


@router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext):
    """Start buyrug'i."""
    await state.clear()
    user = message.from_user
    if user:
        await db.upsert_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
        )

    await message.answer(
        WELCOME_TEXT,
        reply_markup=get_main_reply_keyboard(),
        parse_mode="HTML",
    )


@router.message(Command("help"))
@router.message(F.text == "📖 Qanday ishlaydi?")
async def handle_how_it_works(message: Message):
    """Qanday ishlashi haqida yo'riqnoma."""
    await message.answer(
        HOW_IT_WORKS_TEXT,
        reply_markup=get_main_reply_keyboard(),
        parse_mode="HTML",
    )


@router.message(F.text == "ℹ️ Bot haqida")
async def handle_about(message: Message):
    """Bot haqida ma'lumot."""
    await message.answer(
        ABOUT_BOT_TEXT,
        reply_markup=get_main_reply_keyboard(),
        parse_mode="HTML",
    )


@router.message(F.text == "❌ Bekor qilish")
async def handle_cancel(message: Message, state: FSMContext):
    """Joriy harakatni bekor qilish."""
    await state.clear()
    await message.answer(
        "Amal bekor qilindi. Bosh menyudasiz.",
        reply_markup=get_main_reply_keyboard(),
    )


@router.callback_query(F.data == "main_menu")
async def handle_main_menu_callback(callback: CallbackQuery, state: FSMContext):
    """Bosh menyuga qaytish callback'i."""
    await state.clear()
    await callback.answer()
    if callback.message:
        await callback.message.answer(
            "🏠 Bosh menyu. Nimani xohlaysiz?",
            reply_markup=get_main_reply_keyboard(),
        )
