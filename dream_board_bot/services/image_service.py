"""
AI Tasvir Generatsiyasi Servisi.
OpenAI DALL-E 3 orqali yuqori sifatli vision board tasvirini yaratadi.
Agar API kalit bo'lmasa, soxtalashtirmasdan demo rejimida namuna kartasini tayyorlaydi.
"""

import io
import logging
from typing import Optional, Tuple
import aiohttp
from openai import AsyncOpenAI
from PIL import Image, ImageDraw, ImageFont

from config import config

logger = logging.getLogger(__name__)


class ImageService:
    """Tasvirlarni yaratish va yuklab olish xizmati."""

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

    async def generate_vision_board(
        self,
        prompt: str,
        user_text: str,
        categories: dict[str, str],
        size: Optional[str] = None,
    ) -> Tuple[Optional[bytes], Optional[str], bool, Optional[str]]:
        """
        Orzular xaritasi rasmini yaratadi.
        Qaytaradi: (image_bytes, image_url, is_real_ai, error_message)
        """
        client = self.get_client()

        # Agar haqiqiy OpenAI kaliti bo'lsa
        if client:
            try:
                target_size = size or config.DEFAULT_IMAGE_SIZE
                logger.info(f"DALL-E 3 orqali rasm yaratilmoqda. Prompt uzunligi: {len(prompt)}")
                
                response = await client.images.generate(
                    model=config.OPENAI_MODEL_IMAGE,
                    prompt=prompt,
                    size=target_size,  # masalan '1792x1024'
                    quality=config.DEFAULT_IMAGE_QUALITY,
                    n=1,
                )
                
                image_url = response.data[0].url
                revised_prompt = response.data[0].revised_prompt or prompt
                logger.info("DALL-E 3 dan rasm muvaffaqiyatli olindi.")

                # Rasmni yuklab olamiz
                image_bytes = await self.download_image_bytes(image_url)
                return image_bytes, image_url, True, None

            except Exception as e:
                err_msg = str(e)
                logger.error(f"DALL-E 3 rasm generatsiyasida xatolik: {err_msg}")
                # Foydalanuvchiga tushunarli xabar va zaxira demo rasm
                demo_bytes = self._generate_demo_board_image(user_text, categories)
                return demo_bytes, None, False, f"API xatoligi: {err_msg}"

        # Agar kalit mavjud bo'lmasa -> Demo rejim
        logger.warning("OPENAI_API_KEY o'rnatilmagan. Demo vision board yaratilmoqda.")
        demo_bytes = self._generate_demo_board_image(user_text, categories)
        return demo_bytes, None, False, "OPENAI_API_KEY sozlanmagan"

    async def download_image_bytes(self, url: str) -> Optional[bytes]:
        """Tashqi URL dan rasm baytlarini yuklab oladi."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                    if resp.status == 200:
                        return await resp.read()
                    logger.error(f"Rasm yuklab olishda HTTP xatolik: {resp.status}")
        except Exception as e:
            logger.error(f"Rasm baytlarini yuklab olishda xatolik: {e}")
        return None

    def _generate_demo_board_image(self, user_text: str, categories: dict[str, str]) -> bytes:
        """
        Pillow yordamida to'q ko'k va binafsha gradientli
        zamonaviy Demo Vision Board kartasini yaratadi.
        """
        width, height = 1280, 720
        img = Image.new("RGB", (width, height), color=(15, 23, 42))  # Slate 900
        draw = ImageDraw.Draw(img)

        # Gradient fon effekti
        for y in range(height):
            # To'q ko'kdan (15, 23, 42) binafshagacha (49, 10, 82)
            r = int(15 + (49 - 15) * (y / height))
            g = int(23 + (10 - 23) * (y / height))
            b = int(42 + (82 - 42) * (y / height))
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # Estetik ramkalar va panellar chizish
        # Sarlavha paneli
        draw.rectangle([(60, 40), (width - 60, 130)], fill=(30, 41, 59, 200), outline=(99, 102, 241), width=2)
        
        # Oddiy shrift yoki tizim shriftidan foydalanish
        try:
            # Agar mavjud bo'lsa standart arial yoki default
            title_font = ImageFont.truetype("arial.ttf", 36)
            subtitle_font = ImageFont.truetype("arial.ttf", 20)
            card_title_font = ImageFont.truetype("arial.ttf", 22)
            body_font = ImageFont.truetype("arial.ttf", 16)
        except Exception:
            title_font = subtitle_font = card_title_font = body_font = ImageFont.load_default()

        # Matnlarni chizish
        draw.text((80, 52), "ORZULAR XARITASI — VISION BOARD", fill=(248, 250, 252), font=title_font)
        draw.text((80, 95), "DEMO REJIMI (Haqiqiy AI generatsiyasi uchun .env da OPENAI_API_KEY sozlang)", fill=(245, 158, 11), font=subtitle_font)

        # Orzular kartochkalarini joylashtirish (Grid)
        cols = 3
        margin_x = 60
        margin_y = 160
        card_w = (width - 120 - 40) // cols
        card_h = 220

        category_items = list(categories.items())
        if not category_items:
            category_items = [("maqsad", user_text[:100])]

        for idx, (cat_key, cat_value) in enumerate(category_items[:6]):
            col = idx % cols
            row = idx // cols
            cx = margin_x + col * (card_w + 20)
            cy = margin_y + row * (card_h + 20)

            # Kartochka foni
            draw.rectangle([(cx, cy), (cx + card_w, cy + card_h)], fill=(30, 41, 59), outline=(139, 92, 246), width=2)
            # Kartochka sarlavhasi
            draw.text((cx + 15, cy + 15), f"★ {cat_key.upper()}", fill=(167, 139, 250), font=card_title_font)
            # Kartochka matni
            wrapped_text = self._wrap_text(cat_value, 28)
            draw.text((cx + 15, cy + 55), wrapped_text, fill=(226, 232, 240), font=body_font)

        # Pastki motivatsion chiziq
        draw.rectangle([(60, height - 70), (width - 60, height - 30)], fill=(15, 23, 42), outline=(56, 189, 248), width=1)
        draw.text((80, height - 58), "✨ Kelajak o'z orzularining go'zalligiga ishonganlarnikidir!", fill=(148, 163, 184), font=subtitle_font)

        output = io.BytesIO()
        img.save(output, format="JPEG", quality=90)
        return output.getvalue()

    def _wrap_text(self, text: str, max_chars: int = 30) -> str:
        """Uzun matnni qatorlarga bo'ladi."""
        words = text.split()
        lines = []
        current_line = []
        current_len = 0

        for w in words:
            if current_len + len(w) + 1 > max_chars:
                lines.append(" ".join(current_line))
                current_line = [w]
                current_len = len(w)
            else:
                current_line.append(w)
                current_len += len(w) + 1

        if current_line:
            lines.append(" ".join(current_line))

        return "\n".join(lines[:6])


image_service = ImageService()
