from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from database.db import get_all_user_telegram_ids
from keyboards.keyboards import expert_main_keyboard
from states.states import ExpertState

router = Router()


@router.message(F.text == "📢 E'lon yuborish")
async def broadcast_start(message: Message, state: FSMContext):
    await state.set_state(ExpertState.broadcasting)
    await message.answer(
        "📢 <b>E'lon yozing:</b>\n\n"
        "Matn, rasm, yoki hujjat yuborishingiz mumkin.\n"
        "Bekor qilish uchun: /cancel",
        parse_mode="HTML"
    )


@router.message(ExpertState.broadcasting)
async def send_broadcast(message: Message, state: FSMContext, bot: Bot):
    await state.clear()

    user_ids = await get_all_user_telegram_ids()
    success = 0
    failed = 0

    for user_id in user_ids:
        try:
            await message.copy_to(chat_id=user_id)
            success += 1
        except Exception:
            failed += 1

    await message.answer(
        f"📢 <b>E'lon yuborildi!</b>\n\n"
        f"✅ Muvaffaqiyatli: {success} ta\n"
        f"❌ Yuborilmadi: {failed} ta",
        reply_markup=expert_main_keyboard(),
        parse_mode="HTML"
    )
