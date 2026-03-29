from datetime import datetime, timezone

from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from config import load_config
from database.db import get_user, create_question, is_user_banned, get_last_question_time
from keyboards.keyboards import cancel_keyboard, main_menu_keyboard, answer_question_keyboard
from locales import t
from states.states import UserState
from utils.sanitize import escape

router = Router()

QUESTION_COOLDOWN_SECONDS = 180  # 3 daqiqa
QUESTION_MAX_LENGTH = 2000


@router.message(F.text.in_(["❓ Savol berish", "❓ Задать вопрос"]))
async def ask_question_start(message: Message, state: FSMContext, lang: str):
    # Ban tekshiruvi
    if await is_user_banned(message.from_user.id):
        await message.answer(
            "🚫 Siz bloklangansiz. Savol bera olmaysiz." if lang == "uz"
            else "🚫 Вы заблокированы. Вы не можете задавать вопросы."
        )
        return

    # Rate limit tekshiruvi
    last_time_str = await get_last_question_time(message.from_user.id)
    if last_time_str:
        # SQLite saqlaydi: "YYYY-MM-DD HH:MM:SS" formatida UTC
        last_time = datetime.strptime(last_time_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        elapsed = (now - last_time).total_seconds()
        if elapsed < QUESTION_COOLDOWN_SECONDS:
            remaining = int(QUESTION_COOLDOWN_SECONDS - elapsed)
            mins, secs = divmod(remaining, 60)
            if lang == "uz":
                await message.answer(
                    f"⏳ Keyingi savolni <b>{mins}:{secs:02d}</b> dan keyin bera olasiz.",
                    parse_mode="HTML"
                )
            else:
                await message.answer(
                    f"⏳ Следующий вопрос можно задать через <b>{mins}:{secs:02d}</b>.",
                    parse_mode="HTML"
                )
            return

    await state.set_state(UserState.asking_question)
    await message.answer(
        t("ask_question", lang),
        reply_markup=cancel_keyboard(lang),
        parse_mode="HTML"
    )


@router.message(UserState.asking_question, F.text)
async def receive_question(message: Message, state: FSMContext, lang: str, bot: Bot):
    cancel_texts = [t("btn_cancel", "uz"), t("btn_cancel", "ru")]
    if message.text in cancel_texts:
        await state.clear()
        await message.answer(
            t("question_cancelled", lang),
            reply_markup=main_menu_keyboard(lang)
        )
        return

    if len(message.text) > QUESTION_MAX_LENGTH:
        await message.answer(
            f"❗ Savol juda uzun. Maksimal {QUESTION_MAX_LENGTH} ta belgi." if lang == "uz"
            else f"❗ Вопрос слишком длинный. Максимум {QUESTION_MAX_LENGTH} символов."
        )
        return

    if not message.text.strip():
        return

    question_id = await create_question(
        telegram_id=message.from_user.id,
        text=message.text
    )

    await state.clear()
    await message.answer(
        t("question_sent", lang, question_id=question_id),
        reply_markup=main_menu_keyboard(lang),
        parse_mode="HTML"
    )

    # Ekspertlarga yuborish
    config = load_config()
    user = await get_user(message.from_user.id)
    username_str = f"@{message.from_user.username}" if message.from_user.username else "—"

    expert_text = (
        f"📩 <b>Yangi savol #{question_id}</b>\n\n"
        f"👤 Foydalanuvchi: {escape(message.from_user.full_name)} ({escape(username_str)})\n"
        f"🆔 Telegram ID: <code>{message.from_user.id}</code>\n\n"
        f"💬 <b>Savol:</b>\n{escape(message.text)}"
    )

    for expert_id in config.expert_ids:
        try:
            await bot.send_message(
                chat_id=expert_id,
                text=expert_text,
                reply_markup=answer_question_keyboard(question_id, message.from_user.id, message.from_user.username or ""),
                parse_mode="HTML"
            )
        except Exception:
            pass
