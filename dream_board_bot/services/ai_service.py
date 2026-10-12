"""
AI Matn Tahlili va Prompt Generatsiyasi Servisi.
Foydalanuvchi orzularini tahlil qiladi, toifalarga ajratadi va
DALL-E 3 uchun estetik vision board kollaj promptini shakllantiradi.
"""

import json
import logging
import re
from typing import Any, Optional
from openai import AsyncOpenAI

from config import config

logger = logging.getLogger(__name__)

# Belgilangan 7 ta asosiy toifa va ularning o'zbekcha nomlari
CATEGORIES_UZ = {
    "education": "🎓 Ta’lim va bilim",
    "career": "💼 Kasb va biznes",
    "home_auto": "🏡 Uy va avtomobil",
    "travel": "✈️ Sayohat va kashfiyot",
    "growth": "🌟 Shaxsiy rivojlanish",
    "health": "🏃 Sport va sog‘lom turmush",
    "family": "👨‍👩‍👧 Oila va hayot tarzi",
}


class AIService:
    """Orzularni tahlil qilish va AI prompt yaratish xizmati."""

    def __init__(self):
        self._client: Optional[AsyncOpenAI] = None

    def get_client(self) -> Optional[AsyncOpenAI]:
        """OpenAI asinxron mijozini qaytaradi."""
        if not config.has_openai_key():
            return None
        if self._client is None:
            self._client = AsyncOpenAI(
                api_key=config.OPENAI_API_KEY,
                base_url=config.OPENAI_BASE_URL,
            )
        return self._client

    async def analyze_and_build_prompt(self, user_text: str) -> dict[str, Any]:
        """
        Foydalanuvchi orzulari matnini tahlil qiladi.
        Qaytariladigan ma'lumotlar:
        {
            "categories": {"career": "...", "travel": "..."},
            "formatted_summary": "...",
            "dalle_prompt": "...",
            "is_ai_generated": bool
        }
        """
        client = self.get_client()

        if client:
            try:
                return await self._analyze_with_openai(client, user_text)
            except Exception as e:
                logger.error(f"OpenAI matn tahlilida xatolik: {e}. Zaxira tahlilchiga o'tilmoqda.")

        # OpenAI kaliti bo'lmasa yoki xato bersa, zaxira tahlilchi ishga tushadi
        return self._fallback_analyze(user_text)

    async def _analyze_with_openai(self, client: AsyncOpenAI, user_text: str) -> dict[str, Any]:
        """OpenAI LLM orqali matnni tahlil qilish."""
        system_instruction = (
            "You are an expert Vision Board Art Director and Goal Analyst. "
            "Your task is to analyze user's dreams/goals written in Uzbek and perform two jobs:\n"
            "1. Categorize their goals strictly into available categories: "
            "['education', 'career', 'home_auto', 'travel', 'growth', 'health', 'family']. "
            "Only include categories for which the user actually mentioned goals. DO NOT invent or assume goals not mentioned!\n"
            "2. Generate an extraordinary, professional, aesthetic image generation prompt for DALL-E 3 in English.\n\n"
            "PROMPT REQUIREMENTS for DALL-E 3:\n"
            "- Style: An elegant, high-end, photographic vision board collage / mood board.\n"
            "- Aesthetics: Cinematic golden hour lighting, clean minimalist layout, harmoniously blended photo vignettes.\n"
            "- Composition: A balanced, seamless composition showing photographic representations of ONLY the user's mentioned dreams.\n"
            "- CRITICAL NEGATIVE CONSTRAINTS: Absolutely NO text, NO letters, NO typography, NO watermarks, NO slogans, NO labels, NO blurry artifacts.\n"
            "- Photorealistic, editorial magazine quality, 8k resolution.\n\n"
            "Output MUST be strict JSON in this format:\n"
            "{\n"
            '  "categories": {\n'
            '     "category_key": "user specific goal in Uzbek"\n'
            "  },\n"
            '  "motivation_quote_uz": "Qisqa ilhomlantiruvchi gap (o\'zbek tilida)",\n'
            '  "dalle_prompt": "A photographic aesthetic vision board collage showcasing..."\n'
            "}"
        )

        response = await client.chat.completions.create(
            model=config.OPENAI_MODEL_TEXT,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": f"Foydalanuvchi orzulari:\n{user_text}"},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )

        raw_json = response.choices[0].message.content or "{}"
        data = json.loads(raw_json)

        categories = data.get("categories", {})
        dalle_prompt = data.get("dalle_prompt", "").strip()
        motivation = data.get("motivation_quote_uz", "Har bir orzu aniq maqsad va harakat bilan amalga oshadi!")

        # Agar prompt bo'sh qolsa zaxiradan olamiz
        if not dalle_prompt:
            dalle_prompt = self._construct_artistic_prompt(user_text, categories)

        return {
            "categories": categories,
            "motivation": motivation,
            "dalle_prompt": dalle_prompt,
            "is_ai_generated": True,
        }

    def _fallback_analyze(self, user_text: str) -> dict[str, Any]:
        """
        API kalitsiz yoki oflayn holatda o'zbek tilidagi kalit so'zlar asosida tahlil qilish.
        """
        lower = user_text.lower()
        detected_categories: dict[str, str] = {}

        # Kalit so'zlar qidiruvi
        patterns = {
            "education": [r"ta['’`]?lim", r"o['’`]qi", r"universitet", r"kurs", r"kitob", r"ilm", r"diplom", r"ingliz tili", r"til o['’`]rgan"],
            "career": [r"ish", r"kasb", r"biznes", r"dasturchi", r"kompaniya", r"daromad", r"maosh", r"karyera", r"startup", r"IT", r"loyiha"],
            "home_auto": [r"uy", r"hovli", r"kvartira", r"mashina", r"avto", r"avtomobil", r"bmw", r"mercedes", r"chevrolet", r"gentra", r"villa"],
            "travel": [r"sayohat", r"dunyo", r"maldiv", r"dubay", r"turkiya", r"yevropa", r"aqsh", r"samolyot", r"dengiz", r"tog['’`]"],
            "growth": [r"rivoj", r"maqsad", r"kitob", r"ruhiy", r"shaxsiy", r"tajriba", r"odatlarni", r"erishmoq"],
            "health": [r"sport", r"sog['’`]liq", r"zal", r"fitness", r"yugur", r"vazn", r"badantarbiya", r"taom"],
            "family": [r"oila", r"ota-ona", r"farzand", r"to['’`]y", r"baxt", r"turmush", r"uy-ro['’`]zg['’`]or"]
        }

        for cat_key, regex_list in patterns.items():
            for p in regex_list:
                if re.search(p, lower):
                    # Matndan mos qismni topish yoki umumiy tavsif
                    detected_categories[cat_key] = self._extract_snippet_for_category(user_text, p)
                    break

        if not detected_categories:
            detected_categories["growth"] = user_text[:80] + ("..." if len(user_text) > 80 else "")

        dalle_prompt = self._construct_artistic_prompt(user_text, detected_categories)

        return {
            "categories": detected_categories,
            "motivation": "Orzularingiz sari qadam tashlang — ular albatta haqiqatga aylanadi!",
            "dalle_prompt": dalle_prompt,
            "is_ai_generated": False,
        }

    def _extract_snippet_for_category(self, text: str, pattern: str) -> str:
        """Matndan berilgan mavzuga mos jumla yoki bo'lakni ajratib oladi."""
        sentences = re.split(r"[,;.\n]+", text)
        for s in sentences:
            s_clean = s.strip()
            if re.search(pattern, s_clean, re.IGNORECASE):
                return s_clean.capitalize()
        return "Belgilangan maqsad"

    def _construct_artistic_prompt(self, user_text: str, categories: dict[str, str]) -> str:
        """DALL-E 3 uchun estetik va muvozanatli prompt yaratadi."""
        elements = []
        if "career" in categories:
            elements.append("a sleek modern software engineering workstation with glowing screens")
        if "home_auto" in categories:
            elements.append("a luxury modern minimalist villa with warm evening lights and a luxury sports car parked in driveway")
        if "travel" in categories:
            elements.append("a breathtaking sunny tropical ocean travel destination with turquoise clear water")
        if "education" in categories:
            elements.append("a sophisticated personal library with graduation scrolls and inspiring books")
        if "health" in categories:
            elements.append("an inspiring athletic runner enjoying a sunrise jog")
        if "family" in categories:
            elements.append("a warm and joyful modern family home gathering")
        if "growth" in categories and not elements:
            elements.append("an inspiring mountain peak under golden morning sunlight symbolizing summit of success")

        if not elements:
            elements.append("a vision board of modern luxury living, successful career, and dream travels")

        joined_elements = ", ".join(elements)

        prompt = (
            f"A masterpiece photorealistic vision board collage. Harmonious seamless multi-panel composition "
            f"depicting life goals: {joined_elements}. "
            f"Cinematic aesthetic lighting, warm golden hour sunbeams, elegant color palette with deep navy and rich tones. "
            f"Architectural Digest and National Geographic photography quality, 8k resolution, ultra-detailed, balanced art direction. "
            f"No text, no typography, no watermarks, no distorted objects, no letters."
        )
        return prompt

    def format_analysis_summary(self, categories: dict[str, str], motivation: str, is_ai: bool = True) -> str:
        """Telegramda foydalanuvchiga ko'rsatiladigan chiroyli matn shakli."""
        lines = ["🎯 <b>Aniqlangan maqsad va orzular:</b>\n"]

        for key, text in categories.items():
            title = CATEGORIES_UZ.get(key, f"📌 {key.capitalize()}")
            lines.append(f"• <b>{title}:</b> <i>{text}</i>")

        if not categories:
            lines.append("• <i>Barcha orzularingiz bir butun xaritada mujassamlashdi!</i>")

        lines.append(f"\n✨ <i>«{motivation}»</i>")
        if not is_ai:
            lines.append("\n⚠️ <i>(Tezkor lokal tahlil rejimi)</i>")

        return "\n".join(lines)


ai_service = AIService()
