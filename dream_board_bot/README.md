# 🌟 Orzular Xaritasi AI — Telegram Vision Board Bot

Ushbu loyiha foydalanuvchilarning orzu va maqsadlarini tahlil qilib, **OpenAI (GPT-4o / DALL-E 3)** sun'iy intellekti yordamida professional, estetik va motivatsion **Vision Board (Orzular kollaji)** tasvirini yaratib beruvchi zamonaviy Telegram bot hisoblanadi.

---

## 🚀 Imkoniyatlar va Funksiyalar

1. **Orzularni erkin matnda qabul qilish**:
   - Foydalanuvchi orzularini oddiy o'zbek tilida kiritadi (masalan: *"Men IT dasturchi bo'lishni, yangi uy va avtomobil olishni, Maldivga sayohat qilishni xohlayman"*).
2. **7 ta hayotiy soha bo'yicha aqlli tahlil**:
   - 🎓 *Ta’lim va bilim*
   - 💼 *Kasb va biznes*
   - 🏡 *Uy va avtomobil*
   - ✈️ *Sayohat va kashfiyot*
   - 🌟 *Shaxsiy rivojlanish*
   - 🏃 *Sport va sog‘lom turmush*
   - 👨‍👩‍👧 *Oila va hayot tarzi*
3. **AI Art Direction & DALL-E 3 Prompter**:
   - Belgilangan maqsadlar asosida fotorealistik, kinematik yorug'likka ega, ortiqcha harf va yozuvlarsiz (no text/watermark) muvozanatli estetik kollaj promptini shakllantiradi.
4. **Interaktiv boshqaruv tugmalari**:
   - 🔄 **Qayta yaratish** — shu orzular uchun yangi rakursdagi tasvirni generatsiya qilish.
   - ✏️ **Orzularni o'zgartirish** — matnni tahrirlash va yangilash.
   - 📥 **Asl sifatda yuklab olish** — Telegram siqilmagan holda fayl (document) ko'rinishida yuboradi.
   - 🏠 **Bosh menyu** — asosiy bo'limlarga qaytish.
5. **Generatsiyalar tarixi (SQLite)**:
   - Foydalanuvchi o'zi yaratgan barcha orzular xaritalarini xohlagan vaqtda varaqlab ko'rishi va yuklab olishi mumkin.
6. **Xavfsiz Demo rejim**:
   - Agar OpenAI API kaliti kiritilmagan bo'lsa, tizim soxta AI natijasi bilan aldamaydi, balki ochiq ogohlantirish berib, Pillow kutubxonasida yaratilgan estetik namuna kartasini taqdim etadi.

---

## 📁 Loyiha Strukturasi

```text
dream_board_bot/
├── bot.py                  # Botni ishga tushiruvchi asosiy fayl (Dispatcher & Polling)
├── config.py               # Sozlamalar va .env o'quvchi modul
├── keyboards.py            # Reply va Inline tugmalar
├── handlers/               # Xabarlar va hodisalarni qayta ishlovchi modullar
│   ├── __init__.py         # Routerlarni birlashtiruvchi
│   ├── start.py            # /start, /help, qo'llanma va bot haqida
│   ├── dreams.py           # Orzu kiritish, tahlil, DALL-E generatsiyasi va callbacklar
│   └── history.py          # Rasmlar tarixi va sahifalash
├── services/               # Biznes mantiq va tashqi API integratsiyalari
│   ├── __init__.py
│   ├── ai_service.py       # LLM matn tahlili va DALL-E prompt muhandisligi
│   └── image_service.py    # DALL-E 3 rasm generatsiyasi va Demo generator
├── database/               # Ma'lumotlar bazasi (asinxron SQLite)
│   ├── __init__.py
│   └── db.py               # Foydalanuvchilar va orzular jadvallari
├── test_bot.py             # Avtomatlashtirilgan testlar skripti
├── .env.example            # Muhit o'zgaruvchilari namunasi
├── .gitignore              # Git e'tiborsiz qoldiradigan fayllar
├── requirements.txt        # Kerakli Python kutubxonalari
└── README.md               # To'liq qo'llanma
```

---

## 🛠 O'rnatish va Ishga Tushirish

### 1. Python o'rnatilganligini tekshirish
Bot **Python 3.11+** talab qiladi. Konsolda tekshiring:
```bash
python --version
```

### 2. Virtual muhit yaratish va faollashtirish
Loyihaning asosiy papkasida:
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Kutubxonalarni o'rnatish
```bash
pip install -r dream_board_bot/requirements.txt
```

### 4. Telegram Bot Tokenini olish
1. Telegramda [@BotFather](https://t.me/BotFather) botiga kiring.
2. `/newbot` buyrug'ini yuboring.
3. Botga nom va username bering (masalan: `my_dream_board_ai_bot`).
4. Berilgan HTTP API tokenni nusxalab oling.

### 5. OpenAI API kalitini olish
1. [platform.openai.com](https://platform.openai.com) saytiga kiring.
2. `API Keys` bo'limidan yangi maxfiy kalit (`sk-...`) yarating va nusxalab oling.

### 6. `.env` faylini sozlash
`dream_board_bot/.env.example` faylidan nusxa olib, nomini `.env` ga o'zgartiring:
```bash
# Windows:
copy dream_board_bot\.env.example dream_board_bot\.env

# Linux / Mac:
cp dream_board_bot/.env.example dream_board_bot/.env
```

`.env` faylini ochib, o'z kalitlaringizni kiriting:
```ini
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL_TEXT=gpt-4o-mini
OPENAI_MODEL_IMAGE=dall-e-3
DEFAULT_IMAGE_SIZE=1792x1024
```

### 7. Testlarni ishga tushirish
Tizim to'g'ri sozlanganligini tekshirish uchun:
```bash
python dream_board_bot/test_bot.py
```

### 8. Botni ishga tushirish
`dream_board_bot` papkasiga kiring yoki ildizdan ishga tushiring:
```bash
python dream_board_bot/bot.py
# Yoki:
python run.py
```

---

## ❓ Xatolarni Aniqlash va Hal Qilish (Troubleshooting)

| Xatolik | Sababi | Yechimi |
|---|---|---|
| `BOT_TOKEN ko'rsatilmagan` | `.env` fayli yo'q yoki `BOT_TOKEN` to'ldirilmagan | `.env` fayliga @BotFather dan olingan tokenni joylang. |
| `OpenAI API AuthenticationError (401)` | OpenAI API kaliti noto'g'ri kiritilgan | `OPENAI_API_KEY` to'g'riligini va hisobda balans borligini tekshiring. |
| `OpenAI RateLimitError (429)` | OpenAI so'rovlar chegarasi yoki balans tugagan | Hisobingizni to'ldiring yoki biroz kuting. |
| `Demo rejimida rasm chiqyapti` | `OPENAI_API_KEY` yo'q yoki noto'g'ri | Haqiqiy DALL-E 3 rasmlari uchun `.env` da kalitni ko'rsating. |
| `Telegram Network / Connection Error` | VPN yoki tarmoq cheklovi | Internet ulanishini tekshiring yoki serverda proksi/VPN dan foydalaning. |

---

## 👨‍💻 Muallif va Qo'llab-quvvatlash
Loyiha eng zamonaviy standartlar asosida to'liq asinxron arxitekturada qurilgan. Qo'shimcha savollar yoki yangi funksiyalar qo'shish bo'yicha bemalol murojaat qilishingiz mumkin!
