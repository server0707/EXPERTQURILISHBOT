from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.db import get_user, create_user, update_user_language, get_balance, get_setting
from keyboards.keyboards import language_keyboard, main_menu_keyboard
from locales import t

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, lang: str):
    await state.clear()
    user = await get_user(message.from_user.id)

    if not user:
        await message.answer(
            t("choose_language", "uz"),
            reply_markup=language_keyboard()
        )
        return

    balance = await get_balance(message.from_user.id)
    await message.answer(
        t("welcome", lang, name=message.from_user.first_name, balance=balance),
        reply_markup=main_menu_keyboard(lang),
        parse_mode="HTML"
    )


@router.message(F.text.in_(["📞 Support", "📞 Поддержка"]))
async def show_support(message: Message, lang: str):
    support_username = await get_setting("support_username")
    if not support_username:
        await message.answer(t("support_not_set", lang), parse_mode="HTML")
        return

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await message.answer(
        t("support_info", lang, contact=f"@{support_username}"),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📞 Support", url=f"https://t.me/{support_username}")]
        ])
    )


@router.message(F.text.in_(["🌐 Tilni o'zgartirish", "🌐 Сменить язык"]))
async def change_language_start(message: Message, lang: str):
    await message.answer(
        t("choose_new_language", lang),
        reply_markup=language_keyboard()
    )


@router.callback_query(F.data.startswith("lang:"))
async def choose_language(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split(":")[1] if ":" in callback.data else ""
    if lang not in ("uz", "ru"):
        await callback.answer()
        return

    user = await get_user(callback.from_user.id)
    if not user:
        await create_user(
            telegram_id=callback.from_user.id,
            full_name=callback.from_user.full_name,
            username=callback.from_user.username,
            language=lang,
        )
    else:
        await update_user_language(callback.from_user.id, lang)

    balance = await get_balance(callback.from_user.id)
    await callback.message.edit_text(
        t("welcome", lang, name=callback.from_user.first_name, balance=balance),
        parse_mode="HTML"
    )
    await callback.message.answer(
        t("main_menu", lang),
        reply_markup=main_menu_keyboard(lang)
    )
    await callback.answer()
