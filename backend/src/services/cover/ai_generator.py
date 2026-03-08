import hashlib
import logging
from io import BytesIO
from typing import Optional
import httpx
from src.config import settings

logger = logging.getLogger(__name__)

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class CoverAIGenerator:
    def __init__(self, openai_api_key: Optional[str] = None, use_dalle: bool = True, target_width: int = 180):
        self.target_width = target_width
        self.target_height = int(target_width * 1.5)
        
        api_key = openai_api_key or settings.OPENAI_API_KEY
        
        if use_dalle and OPENAI_AVAILABLE and api_key:
            self.client = AsyncOpenAI(api_key=api_key)
            self.mode = "dalle"
        else:
            self.mode = "placeholder"
            if use_dalle and not OPENAI_AVAILABLE:
                logger.warning("OpenAI not installed, using placeholders")
            elif use_dalle and not api_key:
                logger.warning("OpenAI API key not available, using placeholders")

    async def generate_cover(self, title: str, author: str, isbn: str, genre: Optional[str] = None) -> Optional[bytes]:
        if self.mode == "dalle":
            return await self._generate_dalle(title, author, genre)
        return await self._generate_placeholder(title, author)

    async def _generate_dalle(self, title: str, author: str, genre: Optional[str]) -> Optional[bytes]:
        if not OPENAI_AVAILABLE:
            return None
        genre_hint = f" {genre} style" if genre else ""
        prompt = (
            f"Professional book cover design for '{title}' by {author}.{genre_hint} "
            f"Artistic cover, no text, no letters, no words, "
            f"vertical book cover proportions, high quality, "
            f"minimalist design suitable for 180px thumbnail"
        )
        try:
            response = await self.client.images.generate(model="dall-e-3", prompt=prompt, size="1024x1024", quality="standard", n=1)
            image_url = response.data[0].url
            async with httpx.AsyncClient() as client:
                img_response = await client.get(image_url, timeout=30)
                img_response.raise_for_status()
                return self._resize_image(img_response.content)
        except Exception as e:
            logger.error(f"DALL-E error: {e}")
            return await self._generate_placeholder(title, author)

    async def _generate_placeholder(self, title: str, author: str) -> Optional[bytes]:
        if not PIL_AVAILABLE:
            logger.error("PIL not installed")
            return None
        color_seed = int(hashlib.md5(title.encode()).hexdigest()[:6], 16)
        r, g, b = (color_seed >> 16) & 255, (color_seed >> 8) & 255, color_seed & 255
        r, g, b = max(r, 100), max(g, 100), max(b, 100)
        img = Image.new('RGB', (self.target_width, self.target_height), color=(r, g, b))
        draw = ImageDraw.Draw(img)

        def wrap_text(text: str, max_chars: int = 20) -> list[str]:
            words, lines, current = text.split(), [], ""
            for word in words:
                if len(current) + len(word) < max_chars:
                    current += " " + word if current else word
                else:
                    lines.append(current)
                    current = word
            if current:
                lines.append(current)
            return lines[:3]

        title_lines, y_offset = wrap_text(title, 18), self.target_height // 3
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
        except Exception:
            font_large = font_small = ImageFont.load_default()
        for i, line in enumerate(title_lines):
            bbox = draw.textbbox((0, 0), line, font=font_large)
            x = (self.target_width - (bbox[2] - bbox[0])) // 2
            draw.text((x, y_offset + i * 16), line, fill='white', font=font_large)
        y_author = y_offset + len(title_lines) * 16 + 10
        bbox = draw.textbbox((0, 0), author[:30], font=font_small)
        x = (self.target_width - (bbox[2] - bbox[0])) // 2
        draw.text((x, y_author), author[:30], fill='lightgray', font=font_small)
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        return buffer.getvalue()

    def _resize_image(self, image_data: bytes) -> bytes:
        if not PIL_AVAILABLE:
            return image_data
        img = Image.open(BytesIO(image_data))
        ratio = self.target_width / img.width
        new_height = int(img.height * ratio)
        expected_height = int(self.target_width * 1.5)
        if abs(new_height - expected_height) > 20:
            new_height = expected_height
        img = img.resize((self.target_width, new_height), Image.Resampling.LANCZOS)
        if img.height > expected_height:
            top = (img.height - expected_height) // 2
            img = img.crop((0, top, self.target_width, top + expected_height))
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=90)
        return buffer.getvalue()

    async def close(self) -> None:
        if self.mode == "dalle" and hasattr(self, 'client'):
            await self.client.close()
