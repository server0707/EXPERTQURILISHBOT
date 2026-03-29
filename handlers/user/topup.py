from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from config import load_config
from database.db import get_setting, create_payment, get_payment, get_user
from keyboards.keyboards import cancel_keyboard, main_menu_keyboard, payment_confirm_keyboard
from locales import t
from states.states import UserState
from utils.sanitize import escape

router = Router()


@router.message(F.text.in_(["💳 Balansni to'ldirish", "💳 Пополнить баланс"]))
async def topup_start(message: Message, state: FSMContext, lang: str):
    await state.set_state(UserState.entering_topup_amount)
    await message.answer(
        t("enter_topup_amount", lang),
        reply_markup=cancel_keyboard(lang)
    )


@router.message(UserState.entering_topup_amount, F.text)
async def receive_topup_amount(message: Message, state: FSMContext, lang: str):
    cancel_texts = [t("btn_cancel", "uz"), t("btn_cancel", "ru")]
    if message.text in cancel_texts:
        await state.clear()
        await message.answer(
            t("question_cancelled", lang),
            reply_markup=main_menu_keyboard(lang)
        )
        return

    try:
        amount = int(message.text.replace(" ", "").replace(",", ""))
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer(t("invalid_amount", lang))
        return

    card_number = await get_setting("card_number")
    card_owner = await get_setting("card_owner")

    await state.update_data(topup_amount=amount)
    await state.set_state(UserState.sending_check)

    await message.answer(
        t("send_check", lang, card_number=card_number, card_owner=card_owner, amount=amount),
        reply_markup=cancel_keyboard(lang),
        parse_mode="HTML"
    )


@router.message(UserState.sending_check, F.photo | (F.document & (F.document.mime_type == "application/pdf")))
async def receive_check(message: Message, state: FSMContext, lang: str, bot: Bot):
    data = await state.get_data()
    amount = data.get("topup_amount", 0)

    # file_id olish
    if message.photo:
        file_id = message.photo[-1].file_id
    else:
        file_id = message.document.file_id

    payment_id = await create_payment(
        telegram_id=message.from_user.id,
        amount=amount,
        check_file_id=file_id
    )

    await state.clear()
    await message.answer(
        t("check_sent", lang),
        reply_markup=main_menu_keyboard(lang),
        parse_mode="HTML"
    )

    # Ekspertlarga yuborish
    config = load_config()
    user = await get_user(message.from_user.id)
    username_str = f"@{message.from_user.username}" if message.from_user.username else "—"

    caption = (
        f"💳 <b>Yangi to'lov so'rovi #{payment_id}</b>\n\n"
        f"👤 Foydalanuvchi: {escape(message.from_user.full_name)} ({escape(username_str)})\n"
        f"🆔 Telegram ID: <code>{message.from_user.id}</code>\n"
        f"💰 Miqdor: <b>{amount:,} so'm</b>"
    )

    for expert_id in config.expert_ids:
        try:
            if message.photo:
                await bot.send_photo(
                    chat_id=expert_id,
                    photo=file_id,
                    caption=caption,
                    reply_markup=payment_confirm_keyboard(payment_id),
                    parse_mode="HTML"
                )
            else:
                await bot.send_document(
                    chat_id=expert_id,
                    document=file_id,
                    caption=caption,
                    reply_markup=payment_confirm_keyboard(payment_id),
                    parse_mode="HTML"
                )
        except Exception:
            pass


@router.message(UserState.sending_check, F.document)
async def check_wrong_document(message: Message, lang: str):
    await message.answer(
        "📸 Faqat rasm (foto) yoki PDF fayl yuboring." if lang == "uz"
        else "📸 Отправьте только фото или PDF-файл."
    )


@router.message(UserState.sending_check, F.text)
async def check_text_not_accepted(message: Message, state: FSMContext, lang: str):
    cancel_texts = [t("btn_cancel", "uz"), t("btn_cancel", "ru")]
    if message.text in cancel_texts:
        await state.clear()
        await message.answer(
            t("question_cancelled", lang),
            reply_markup=main_menu_keyboard(lang)
        )
        return

    await message.answer(
        "📸 Faqat rasm (foto) yoki PDF fayl yuboring." if lang == "uz"
        else "📸 Отправьте только фото или PDF-файл."
    )
