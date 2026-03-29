import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

from config import load_config
from database.db import init_db
from middlewares.language import LanguageMiddleware

from handlers.user import start, questions, balance, topup
from handlers.expert import answers, topup as expert_topup, broadcast, settings as expert_settings, moderation

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    config = load_config()

    await init_db(config.db_path)
    logger.info("Database initialized.")

    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Middleware
    dp.message.middleware(LanguageMiddleware())
    dp.callback_query.middleware(LanguageMiddleware())

    # Expert filter — faqat expert_ids uchun ishlaydi
    from aiogram.filters import Filter
    from aiogram.types import TelegramObject

    class ExpertFilter(Filter):
        async def __call__(self, event: TelegramObject, **data) -> bool:
            from_user = data.get("event_from_user")
            return from_user and from_user.id in config.expert_ids

    # /cancel command — universal
    @dp.message(Command("cancel"))
    async def cmd_cancel(message: Message, state, lang: str):
        from aiogram.fsm.context import FSMContext
        from keyboards.keyboards import expert_main_keyboard, main_menu_keyboard
        current_state = await state.get_state()
        if current_state:
            await state.clear()
        if message.from_user.id in config.expert_ids:
            await message.answer("❌ Bekor qilindi.", reply_markup=expert_main_keyboard())
        else:
            await message.answer("❌ Bekor qilindi.", reply_markup=main_menu_keyboard(lang))

    # Expert routerlariga filter qo'shish
    answers.router.message.filter(ExpertFilter())
    answers.router.callback_query.filter(ExpertFilter())
    expert_topup.router.callback_query.filter(ExpertFilter())
    broadcast.router.message.filter(ExpertFilter())
    expert_settings.router.message.filter(ExpertFilter())
    expert_settings.router.callback_query.filter(ExpertFilter())
    moderation.router.message.filter(ExpertFilter())
    moderation.router.callback_query.filter(ExpertFilter())

    # Expert /start
    @dp.message(Command("start"), ExpertFilter())
    async def expert_start(message: Message, state):
        from aiogram.fsm.context import FSMContext
        from keyboards.keyboards import expert_main_keyboard
        await state.clear()
        await message.answer(
            f"👨‍💼 Salom, ekspert!\n\nBoshqaruv paneli:",
            reply_markup=expert_main_keyboard()
        )

    # Routerlarni ro'yxatdan o'tkazish
    # Expert routerlari avval (aniqroq filterlar)
    dp.include_router(answers.router)
    dp.include_router(expert_topup.router)
    dp.include_router(broadcast.router)
    dp.include_router(expert_settings.router)
    dp.include_router(moderation.router)

    # User routerlari
    dp.include_router(start.router)
    dp.include_router(questions.router)
    dp.include_router(balance.router)
    dp.include_router(topup.router)

    logger.info("Bot ishga tushmoqda...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
