from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery

from database.db import (
    get_payment, update_payment_status,
    change_balance, get_balance, get_awaiting_payment_questions,
    get_answer_by_question, update_question_status, get_user
)
from database.models import PaymentStatus, QuestionStatus
from keyboards.keyboards import expert_main_keyboard
from locales import t
from utils.sanitize import escape

router = Router()


@router.callback_query(F.data.startswith("payment:confirm:"))
async def confirm_payment(callback: CallbackQuery, bot: Bot):
    try:
        payment_id = int(callback.data.split(":")[2])
    except (IndexError, ValueError):
        await callback.answer("Noto'g'ri so'rov!", show_alert=True)
        return

    payment = await get_payment(payment_id)

    if not payment:
        await callback.answer("To'lov topilmadi!", show_alert=True)
        return

    # Atomik yangilash: faqat hali PENDING bo'lsa o'zgaradi
    updated = await update_payment_status(payment_id, PaymentStatus.CONFIRMED, callback.from_user.id)
    if not updated:
        await callback.answer("Bu to'lov allaqachon ko'rib chiqilgan!", show_alert=True)
        return

    user_telegram_id = payment["user_telegram_id"]
    amount = payment["amount"]

    await change_balance(
        telegram_id=user_telegram_id,
        amount=amount,
        description=f"To'lov #{payment_id} tasdiqlandi"
    )

    new_balance = await get_balance(user_telegram_id)
    user = await get_user(user_telegram_id)
    user_lang = user.get("language", "uz") if user else "uz"

    # Foydalanuvchiga xabar
    await bot.send_message(
        chat_id=user_telegram_id,
        text=t("topup_confirmed", user_lang, amount=amount, balance=new_balance),
        parse_mode="HTML"
    )

    # awaiting_payment savollarini tekshirish va yetkazish
    await deliver_pending_answers(bot, user_telegram_id, user_lang)

    await callback.message.edit_caption(
        caption=(callback.message.caption or "") + f"\n\n✅ <b>Tasdiqlandi</b> (@{callback.from_user.username})",
        parse_mode="HTML"
    )
    await callback.answer("✅ To'lov tasdiqlandi!")


@router.callback_query(F.data.startswith("payment:reject:"))
async def reject_payment(callback: CallbackQuery, bot: Bot):
    try:
        payment_id = int(callback.data.split(":")[2])
    except (IndexError, ValueError):
        await callback.answer("Noto'g'ri so'rov!", show_alert=True)
        return

    payment = await get_payment(payment_id)

    if not payment:
        await callback.answer("To'lov topilmadi!", show_alert=True)
        return

    user_telegram_id = payment["user_telegram_id"]
    user = await get_user(user_telegram_id)
    user_lang = user.get("language", "uz") if user else "uz"

    updated = await update_payment_status(payment_id, PaymentStatus.REJECTED, callback.from_user.id)
    if not updated:
        await callback.answer("Bu to'lov allaqachon ko'rib chiqilgan!", show_alert=True)
        return

    await bot.send_message(
        chat_id=user_telegram_id,
        text=t("topup_rejected", user_lang),
        parse_mode="HTML"
    )

    await callback.message.edit_caption(
        caption=(callback.message.caption or "") + f"\n\n❌ <b>Rad etildi</b> (@{callback.from_user.username})",
        parse_mode="HTML"
    )
    await callback.answer("❌ To'lov rad etildi.")


async def deliver_pending_answers(bot: Bot, user_telegram_id: int, user_lang: str):
    """Balans to'ldirilgandan keyin awaiting_payment savollarni yetkazish"""
    pending = await get_awaiting_payment_questions(user_telegram_id)

    for question in pending:
        question_id = question["id"]
        price = question["price"]
        current_balance = await get_balance(user_telegram_id)

        if current_balance >= price:
            await update_question_status(question_id, QuestionStatus.DELIVERED)
            await change_balance(
                telegram_id=user_telegram_id,
                amount=-price,
                description=f"Savol #{question_id} uchun to'lov"
            )
            new_balance = await get_balance(user_telegram_id)

            await bot.send_message(
                chat_id=user_telegram_id,
                text=t("answer_delivered", user_lang,
                       question_id=question_id,
                       question_text=escape(question["text"]),
                       answer_text=escape(question["answer_text"]),
                       price=price,
                       balance=new_balance),
                parse_mode="HTML"
            )
        else:
            # Hali ham yetarli emas, yangi deficit xabari
            deficit = price - current_balance
            await bot.send_message(
                chat_id=user_telegram_id,
                text=t("answer_awaiting_payment", user_lang,
                       question_id=question_id,
                       price=price,
                       balance=current_balance,
                       deficit=deficit),
                parse_mode="HTML"
            )
