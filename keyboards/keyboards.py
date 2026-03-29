from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from locales import t


def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang:uz"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
        ]
    ])


def main_menu_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("btn_ask", lang))],
            [KeyboardButton(text=t("btn_balance", lang)), KeyboardButton(text=t("btn_topup", lang))],
            [KeyboardButton(text=t("btn_support", lang)), KeyboardButton(text=t("btn_language", lang))],
        ],
        resize_keyboard=True,
    )


def cancel_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t("btn_cancel", lang))]],
        resize_keyboard=True,
    )


# ─────────────────────── EXPERT KEYBOARDS ───────────────────────

def expert_main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Kutayotgan savollar")],
            [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="🚫 Ban boshqaruvi")],
            [KeyboardButton(text="📢 E'lon yuborish"), KeyboardButton(text="⚙️ Sozlamalar")],
        ],
        resize_keyboard=True,
    )


def payment_confirm_keyboard(payment_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"payment:confirm:{payment_id}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"payment:reject:{payment_id}"),
        ]
    ])


def answer_question_keyboard(question_id: int, user_telegram_id: int = 0, username: str = "") -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text="✍️ Javob yozish", callback_data=f"answer:{question_id}")],
    ]
    if user_telegram_id:
        action_row = [
            InlineKeyboardButton(text="🚫 Ban qilish", callback_data=f"ban:quick:{user_telegram_id}"),
        ]
        if username:
            action_row.insert(0, InlineKeyboardButton(
                text="✉️ Foydalanuvchiga yozish",
                url=f"https://t.me/{username}"
            ))
        rows.append(action_row)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def settings_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Karta raqamini o'zgartirish", callback_data="settings:card_number")],
        [InlineKeyboardButton(text="👤 Karta egasini o'zgartirish", callback_data="settings:card_owner")],
        [InlineKeyboardButton(text="📞 Support username", callback_data="settings:support_username")],
    ])


def ban_management_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚫 User ban qilish", callback_data="ban:ban_user")],
        [InlineKeyboardButton(text="✅ Unban qilish", callback_data="ban:unban_user")],
        [InlineKeyboardButton(text="📋 Banlangan userlar", callback_data="ban:list")],
    ])
