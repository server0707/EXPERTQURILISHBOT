from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from database.db import get_user


class LanguageMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        tg_user: User | None = data.get("event_from_user")
        lang = "uz"

        if tg_user:
            user = await get_user(tg_user.id)
            if user:
                raw_lang = user.get("language", "uz")
                lang = raw_lang if raw_lang in ("uz", "ru") else "uz"

        data["lang"] = lang
        return await handler(event, data)
