"""
Middleware для автоматической инъекции конфигурации в обработчики.
"""
import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.config import Config

logger = logging.getLogger(__name__)


class ConfigMiddleware(BaseMiddleware):
    """Middleware для добавления конфигурации в каждый обработчик."""

    def __init__(self, config: Config) -> None:
        self.config = config
        logger.debug("Config Middleware initialized.")

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        # Добавляем конфигурацию в data
        data["config"] = self.config
        
        # Вызываем следующий обработчик
        return await handler(event, data)
