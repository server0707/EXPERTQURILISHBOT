from aiogram import Router, F
from aiogram.types import Message

from database.db import get_balance
from keyboards.keyboards import main_menu_keyboard
from locales import t

router = Router()


@router.message(F.text.in_(["💰 Balans", "💰 Баланс"]))
async def show_balance(message: Message, lang: str):
    balance = await get_balance(message.from_user.id)
    await message.answer(
        t("balance_info", lang, balance=balance),
        reply_markup=main_menu_keyboard(lang),
        parse_mode="HTML"
    )
