import html
import re

# 16 ta raqam, bo'shliq yoki tire bilan guruhlangan yoki guruhlanmagan
# Qabul qilinadi: "8600123456789012", "8600 1234 5678 9012", "8600-1234-5678-9012"
_CARD_RE = re.compile(r"^\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}$")

# Karta egasi: faqat harf (lotin/kirill), bo'shliq, apostrof, tire
_OWNER_RE = re.compile(r"^[\w\s'\-]{2,64}$", re.UNICODE)


def escape(text: str) -> str:
    """
    Foydalanuvchidan kelgan barcha matnni HTML xavfli belgilardan tozalaydi.
    Telegram HTML parse_mode bilan yuborishdan oldin ishlatiladi.
    <, >, &, ", ' → &lt; &gt; &amp; &quot; &#x27;
    """
    return html.escape(str(text))


def validate_card_number(text: str) -> tuple[bool, str]:
    """
    Karta raqamini tekshiradi.
    Qaytaradi: (ok, normalized)
    normalized — standart ko'rinish: "XXXX XXXX XXXX XXXX"
    """
    cleaned = text.strip()
    if not _CARD_RE.match(cleaned):
        return False, ""
    digits = re.sub(r"[\s\-]", "", cleaned)
    normalized = " ".join(digits[i:i+4] for i in range(0, 16, 4))
    return True, normalized


def validate_card_owner(text: str) -> tuple[bool, str]:
    """
    Karta egasi ismini tekshiradi.
    Faqat harf, bo'shliq, apostrof va tire ruxsat etiladi.
    """
    cleaned = text.strip()
    if not _OWNER_RE.match(cleaned):
        return False, ""
    return True, cleaned
