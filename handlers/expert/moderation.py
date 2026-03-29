from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

from database.db import (
    get_statistics, ban_user, unban_user, get_banned_users, get_user
)
from keyboards.keyboards import expert_main_keyboard, ban_management_keyboard
from states.states import ExpertState
from utils.sanitize import escape

CANCEL_TEXT = "❌ Bekor qilish"


def cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=CANCEL_TEXT)]],
        resize_keyboard=True
    )

router = Router()


# ─────────────────────────── STATISTIKA ───────────────────────────

@router.message(F.text == "📊 Statistika")
async def show_statistics(message: Message):
    stats = await get_statistics()
    text = (
        f"📊 <b>Bot statistikasi</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{stats['total_users']}</b>\n"
        f"🚫 Banlangan: <b>{stats['banned_users']}</b>\n\n"
        f"❓ Jami savollar: <b>{stats['total_questions']}</b>\n"
        f"⏳ Kutayotgan savollar: <b>{stats['pending_questions']}</b>\n"
        f"✅ Javob yetkazilgan: <b>{stats['delivered_questions']}</b>\n\n"
        f"💳 To'lov kutayotgan: <b>{stats['pending_payments']}</b>\n"
        f"✅ Tasdiqlangan to'lovlar: <b>{stats['confirmed_payments']}</b>\n"
        f"💰 Jami to'ldirilgan: <b>{stats['total_topup']:,} so'm</b>"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=expert_main_keyboard())


# ─────────────────────────── BAN BOSHQARUVI ───────────────────────────

@router.message(F.text == "🚫 Ban boshqaruvi")
async def ban_management(message: Message):
    await message.answer(
        "🚫 <b>Ban boshqaruvi</b>\n\nQuyidagi amallardan birini tanlang:",
        parse_mode="HTML",
        reply_markup=ban_management_keyboard()
    )


@router.callback_query(F.data.startswith("ban:quick:"))
async def ban_user_quick(callback: CallbackQuery, bot: Bot):
    try:
        target_id = int(callback.data.split(":")[2])
    except (IndexError, ValueError):
        await callback.answer("Noto'g'ri so'rov!", show_alert=True)
        return
    user = await get_user(target_id)
    if not user:
        await callback.answer("Foydalanuvchi topilmadi!", show_alert=True)
        return

    from database.db import is_user_banned
    if await is_user_banned(target_id):
        await callback.answer("Bu foydalanuvchi allaqachon banlangan.", show_alert=True)
        return

    await ban_user(target_id)
    username_str = f"@{user['username']}" if user['username'] else "—"
    await callback.answer(
        f"🚫 {user['full_name']} ban qilindi.", show_alert=True
    )
    await callback.message.reply(
        f"🚫 <b>{escape(user['full_name'])}</b> ({escape(username_str)}) ban qilindi.\n"
        f"ID: <code>{target_id}</code>",
        parse_mode="HTML"
    )
    try:
        await bot.send_message(
            chat_id=target_id,
            text="🚫 Siz bloklangansiz. Savol bera olmaysiz."
        )
    except Exception:
        pass


@router.callback_query(F.data == "ban:ban_user")
async def ban_user_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ExpertState.banning_user)
    await callback.message.answer(
        "🚫 Ban qilmoqchi bo'lgan foydalanuvchining <b>Telegram ID</b>sini kiriting:",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "ban:unban_user")
async def unban_user_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ExpertState.unbanning_user)
    await callback.message.answer(
        "✅ Unban qilmoqchi bo'lgan foydalanuvchining <b>Telegram ID</b>sini kiriting:",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "ban:list")
async def list_banned_users(callback: CallbackQuery):
    banned = await get_banned_users()
    if not banned:
        await callback.message.answer("✅ Hozircha hech kim banlangan emas.")
    else:
        lines = []
        for u in banned:
            uname = f"@{u['username']}" if u['username'] else "—"
            lines.append(
                f"• {escape(u['full_name'])} ({escape(uname)})\n"
                f"  ID: <code>{u['telegram_id']}</code>"
            )
        await callback.message.answer(
            f"🚫 <b>Banlangan foydalanuvchilar ({len(banned)} ta):</b>\n\n" + "\n\n".join(lines),
            parse_mode="HTML"
        )
    await callback.answer()


@router.message(ExpertState.banning_user, F.text)
async def do_ban_user(message: Message, state: FSMContext, bot: Bot):
    if message.text == CANCEL_TEXT:
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=expert_main_keyboard())
        return

    try:
        target_id = int(message.text.strip())
    except ValueError:
        await message.answer("❗ Faqat raqam kiriting (Telegram ID):")
        return

    user = await get_user(target_id)
    if not user:
        await message.answer(
            f"❗ <code>{target_id}</code> ID li foydalanuvchi topilmadi.",
            parse_mode="HTML"
        )
        await state.clear()
        return

    await ban_user(target_id)
    await state.clear()

    username_str = f"@{user['username']}" if user['username'] else "—"
    await message.answer(
        f"🚫 <b>{escape(user['full_name'])}</b> ({escape(username_str)}) ban qilindi.\n"
        f"ID: <code>{target_id}</code>",
        parse_mode="HTML",
        reply_markup=expert_main_keyboard()
    )

    try:
        await bot.send_message(
            chat_id=target_id,
            text="🚫 Siz bloklangansiz. Savol bera olmaysiz."
        )
    except Exception:
        pass


@router.message(ExpertState.unbanning_user, F.text)
async def do_unban_user(message: Message, state: FSMContext, bot: Bot):
    if message.text == CANCEL_TEXT:
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=expert_main_keyboard())
        return

    try:
        target_id = int(message.text.strip())
    except ValueError:
        await message.answer("❗ Faqat raqam kiriting (Telegram ID):")
        return

    user = await get_user(target_id)
    if not user:
        await message.answer(
            f"❗ <code>{target_id}</code> ID li foydalanuvchi topilmadi.",
            parse_mode="HTML"
        )
        await state.clear()
        return

    await unban_user(target_id)
    await state.clear()

    username_str = f"@{user['username']}" if user['username'] else "—"
    await message.answer(
        f"✅ <b>{escape(user['full_name'])}</b> ({escape(username_str)}) unban qilindi.\n"
        f"ID: <code>{target_id}</code>",
        parse_mode="HTML",
        reply_markup=expert_main_keyboard()
    )

    try:
        await bot.send_message(
            chat_id=target_id,
            text="✅ Bloklash olib tashlandi. Endi savol bera olasiz."
        )
    except Exception:
        pass
