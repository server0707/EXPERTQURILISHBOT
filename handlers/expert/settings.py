from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.db import get_setting, set_setting
from keyboards.keyboards import expert_main_keyboard, settings_keyboard
from states.states import ExpertState
from utils.sanitize import validate_card_number, validate_card_owner

SUPPORT_USERNAME_MAX = 64

router = Router()


@router.message(F.text == "⚙️ Sozlamalar")
async def show_settings(message: Message):
    card_number = await get_setting("card_number")
    card_owner = await get_setting("card_owner")
    support_username = await get_setting("support_username") or "—"

    await message.answer(
        f"⚙️ <b>Sozlamalar</b>\n\n"
        f"💳 Karta raqami: <code>{card_number}</code>\n"
        f"👤 Karta egasi: <b>{card_owner}</b>\n"
        f"📞 Support: <b>{support_username}</b>",
        reply_markup=settings_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "settings:card_number")
async def change_card_number_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ExpertState.changing_card_number)
    await callback.message.answer(
        "💳 Yangi karta raqamini kiriting:\n"
        "<i>Masalan: 8600 1234 5678 9012</i>",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(ExpertState.changing_card_number, F.text)
async def save_card_number(message: Message, state: FSMContext):
    ok, normalized = validate_card_number(message.text)
    if not ok:
        await message.answer(
            "❗ Noto'g'ri karta raqami!\n"
            "16 ta raqam kiriting.\n"
            "<i>Masalan: 8600 1234 5678 9012</i>",
            parse_mode="HTML"
        )
        return
    await state.clear()
    await set_setting("card_number", normalized)
    await message.answer(
        f"✅ Karta raqami yangilandi:\n<code>{normalized}</code>",
        reply_markup=expert_main_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "settings:card_owner")
async def change_card_owner_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ExpertState.changing_card_owner)
    await callback.message.answer(
        "👤 Karta egasining ismini kiriting:\n"
        "<i>Masalan: Abdullayev Bobur</i>",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(ExpertState.changing_card_owner, F.text)
async def save_card_owner(message: Message, state: FSMContext):
    ok, cleaned = validate_card_owner(message.text)
    if not ok:
        await message.answer(
            "❗ Noto'g'ri ism!\n"
            "Faqat harf, bo'shliq va tire ishlatilsin (2–64 belgi).\n"
            "<i>Masalan: Abdullayev Bobur</i>",
            parse_mode="HTML"
        )
        return
    await state.clear()
    await set_setting("card_owner", cleaned)
    await message.answer(
        f"✅ Karta egasi yangilandi: <b>{cleaned}</b>",
        reply_markup=expert_main_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "settings:support_username")
async def change_support_username_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ExpertState.changing_support_username)
    await callback.message.answer(
        "📞 Support uchun Telegram username kiriting:\n"
        "<i>Masalan: @support_agent yoki https://t.me/support_agent</i>\n\n"
        "O'chirish uchun: <code>-</code> yuboring",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(ExpertState.changing_support_username, F.text)
async def save_support_username(message: Message, state: FSMContext):
    text = message.text.strip()

    if text == "-":
        await state.clear()
        await set_setting("support_username", "")
        await message.answer(
            "✅ Support manzili o'chirildi.",
            reply_markup=expert_main_keyboard()
        )
        return

    # @ va https://t.me/ ni normallashtirish
    if text.startswith("https://t.me/"):
        username = text[len("https://t.me/"):]
    elif text.startswith("@"):
        username = text[1:]
    else:
        username = text

    if not username or len(username) > SUPPORT_USERNAME_MAX or not username.replace("_", "").isalnum():
        await message.answer(
            "❗ Noto'g'ri username. Faqat harf, raqam va _ ishlatilsin.\n"
            "<i>Masalan: @support_agent</i>",
            parse_mode="HTML"
        )
        return

    await state.clear()
    await set_setting("support_username", username)
    await message.answer(
        f"✅ Support yangilandi: @{username}",
        reply_markup=expert_main_keyboard()
    )
