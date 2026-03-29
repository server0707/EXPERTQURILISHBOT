from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.db import (
    get_question, create_answer, update_question_status,
    get_balance, change_balance, get_user
)
from database.models import QuestionStatus
from keyboards.keyboards import expert_main_keyboard, main_menu_keyboard
from locales import t
from states.states import ExpertState
from utils.sanitize import escape

router = Router()


@router.callback_query(F.data.startswith("answer:"))
async def answer_start(callback: CallbackQuery, state: FSMContext):
    try:
        question_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer("Noto'g'ri so'rov!", show_alert=True)
        return

    # Agar ekspert allaqachon boshqa jarayonda bo'lsa
    current_state = await state.get_state()
    if current_state is not None:
        await callback.answer(
            "Avval joriy jarayonni /cancel bilan bekor qiling.",
            show_alert=True
        )
        return

    question = await get_question(question_id)

    if not question:
        await callback.answer("Savol topilmadi!", show_alert=True)
        return

    if question["status"] != QuestionStatus.PENDING:
        await callback.answer("Bu savolga allaqachon javob berilgan!", show_alert=True)
        return

    await state.set_state(ExpertState.writing_answer)
    await state.update_data(question_id=question_id)

    await callback.message.answer(
        f"✍️ <b>#{question_id}</b> savolga javob yozing:\n\n"
        f"<b>Savol:</b> {escape(question['text'])}",
        parse_mode="HTML"
    )
    await callback.answer()


ANSWER_MAX_LENGTH = 4000


@router.message(ExpertState.writing_answer, F.text)
async def receive_answer_text(message: Message, state: FSMContext):
    if len(message.text) > ANSWER_MAX_LENGTH:
        await message.answer(f"❗ Javob juda uzun. Maksimal {ANSWER_MAX_LENGTH} ta belgi.")
        return

    if not message.text.strip():
        return

    data = await state.get_data()
    question_id = data.get("question_id")

    await state.update_data(answer_text=message.text)
    await state.set_state(ExpertState.entering_price)

    await message.answer(
        f"💰 Bu javob narxini kiriting (so'mda):\n"
        f"<i>0 kiritsangiz — bepul</i>",
        parse_mode="HTML"
    )


@router.message(ExpertState.entering_price, F.text)
async def receive_price(message: Message, state: FSMContext, bot: Bot):
    try:
        price = int(message.text.replace(" ", "").replace(",", ""))
        if price < 0:
            raise ValueError
    except ValueError:
        await message.answer("❗ Faqat musbat raqam yoki 0 kiriting:")
        return

    data = await state.get_data()
    question_id = data.get("question_id")
    answer_text = data.get("answer_text")

    await state.clear()

    question = await get_question(question_id)
    if not question:
        await message.answer("❗ Savol topilmadi.")
        return

    user_telegram_id = question["user_telegram_id"]
    user = await get_user(user_telegram_id)
    user_lang = user.get("language", "uz") if user else "uz"
    user_balance = question["balance"]

    # Javobni saqlash
    await create_answer(
        question_id=question_id,
        expert_telegram_id=message.from_user.id,
        text=answer_text,
        price=price
    )

    q_text = escape(question["text"])
    a_text = escape(answer_text)

    if price == 0:
        # Bepul — darhol yetkazish
        await update_question_status(question_id, QuestionStatus.DELIVERED)
        await bot.send_message(
            chat_id=user_telegram_id,
            text=t("answer_free", user_lang,
                   question_id=question_id,
                   question_text=q_text,
                   answer_text=a_text),
            parse_mode="HTML"
        )
        await message.answer(
            f"✅ Javob #{question_id} bepul yuborildi.",
            reply_markup=expert_main_keyboard()
        )

    elif user_balance >= price:
        # Balans yetarli — darhol yetkazish
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
                   question_text=q_text,
                   answer_text=a_text,
                   price=price,
                   balance=new_balance),
            parse_mode="HTML"
        )
        await message.answer(
            f"✅ Javob #{question_id} yuborildi. {price:,} so'm yechildi.",
            reply_markup=expert_main_keyboard()
        )

    else:
        # Balans yetarli emas — kutish holatiga o'tkazish
        await update_question_status(question_id, QuestionStatus.AWAITING_PAYMENT)
        deficit = price - user_balance
        await bot.send_message(
            chat_id=user_telegram_id,
            text=t("answer_awaiting_payment", user_lang,
                   question_id=question_id,
                   price=price,
                   balance=user_balance,
                   deficit=deficit),
            parse_mode="HTML"
        )
        await message.answer(
            f"⏳ #{question_id} uchun javob saqlandi.\n"
            f"Foydalanuvchi balansi yetarli emas ({user_balance:,} so'm / {price:,} so'm).\n"
            f"Balans to'ldirilgach avtomatik yetkaziladi.",
            reply_markup=expert_main_keyboard()
        )


@router.message(F.text == "📋 Kutayotgan savollar")
async def list_pending_questions(message: Message):
    from database.db import get_pending_questions
    questions = await get_pending_questions()

    if not questions:
        await message.answer("✅ Hozircha barcha savollarga javob berilgan.")
        return

    await message.answer(f"📋 <b>Kutayotgan savollar: {len(questions)} ta</b>", parse_mode="HTML")

    from keyboards.keyboards import answer_question_keyboard
    for q in questions[:10]:
        username_str = f"@{q['username']}" if q.get('username') else "—"
        try:
            await message.answer(
                f"<b>#{q['id']}</b> — {escape(q['full_name'])} ({escape(username_str)})\n"
                f"🆔 <code>{q['user_telegram_id']}</code>\n\n"
                f"{escape(q['text'])}",
                reply_markup=answer_question_keyboard(q['id'], q['user_telegram_id'], q.get('username') or ""),
                parse_mode="HTML"
            )
        except Exception:
            await message.answer(
                f"<b>#{q['id']}</b> — {escape(q['full_name'])}\n"
                f"🆔 <code>{q['user_telegram_id']}</code>\n\n"
                f"{escape(q['text'])}",
                reply_markup=answer_question_keyboard(q['id']),
                parse_mode="HTML"
            )
