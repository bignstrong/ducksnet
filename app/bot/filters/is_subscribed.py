"""
Фильтр для проверки подписки на канал.
"""
import logging
from typing import Any, Dict, Union

from aiogram import Bot
from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message

from app.config import Config

logger = logging.getLogger(__name__)


class IsSubscribed(BaseFilter):
    """
    Фильтр для проверки подписки пользователя на канал.
    Возвращает True, если пользователь подписан или если проверка подписки отключена.
    """

    def __init__(self) -> None:
        self.name = "is_subscribed"

    async def __call__(
        self,
        event: Union[Message, CallbackQuery],
        config: Config,
        bot: Bot,
    ) -> bool:
        # Если принудительная подписка отключена, пропускаем всех
        if not config.shop.FORCE_SUBSCRIPTION_ENABLED:
            return True

        user_id = event.from_user.id

        # Получаем ID канала
        channel_id = config.shop.FORCE_SUBSCRIPTION_CHANNEL_ID
        if not channel_id and config.shop.FORCE_SUBSCRIPTION_CHANNEL_USERNAME:
            channel_id = f"@{config.shop.FORCE_SUBSCRIPTION_CHANNEL_USERNAME}"

        if not channel_id:
            logger.warning("Channel ID or username not configured for force subscription")
            return True

        try:
            # Проверяем статус участника канала
            member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            
            # Проверяем статус подписки
            is_subscribed = member.status in [
                "member",
                "administrator", 
                "creator"
            ]
            
            if is_subscribed:
                logger.debug(f"User {user_id} is subscribed to channel {channel_id}")
            else:
                logger.info(f"User {user_id} is not subscribed to channel {channel_id}, status: {member.status}")
            
            return is_subscribed

        except Exception as e:
            logger.error(f"Error checking subscription for user {user_id} in channel {channel_id}: {e}")
            # В случае ошибки (например, бот не в канале), пропускаем пользователя
            return True


class NotSubscribed(BaseFilter):
    """
    Фильтр для выявления неподписанных пользователей.
    Возвращает True, если пользователь НЕ подписан и проверка подписки включена.
    """

    def __init__(self) -> None:
        self.name = "not_subscribed"

    async def __call__(
        self,
        event: Union[Message, CallbackQuery],
        config: Config,
        bot: Bot,
    ) -> Dict[str, Any]:
        # Если принудительная подписка отключена, никого не блокируем
        if not config.shop.FORCE_SUBSCRIPTION_ENABLED:
            return False

        user_id = event.from_user.id

        # Получаем ID канала
        channel_id = config.shop.FORCE_SUBSCRIPTION_CHANNEL_ID
        channel_username = config.shop.FORCE_SUBSCRIPTION_CHANNEL_USERNAME
        
        if not channel_id and channel_username:
            channel_id = f"@{channel_username}"

        if not channel_id:
            logger.warning("Channel ID or username not configured for force subscription")
            return False

        try:
            # Проверяем статус участника канала
            member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            
            # Проверяем статус подписки
            is_subscribed = member.status in [
                "member",
                "administrator", 
                "creator"
            ]
            
            if not is_subscribed:
                logger.info(f"User {user_id} is not subscribed to channel {channel_id}, blocking access")
                return {
                    "channel_id": channel_id,
                    "channel_username": channel_username,
                    "user_status": member.status
                }
            
            return False

        except Exception as e:
            logger.error(f"Error checking subscription for user {user_id} in channel {channel_id}: {e}")
            # В случае ошибки (например, бот не в канале), не блокируем пользователя
            return False
