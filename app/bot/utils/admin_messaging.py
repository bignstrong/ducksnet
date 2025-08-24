"""
Утилиты для админских сообщений без изображений.
"""
import logging
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup

logger = logging.getLogger(__name__)


async def edit_admin_message(
    callback: CallbackQuery,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    """
    Редактирует сообщение для админки без изображений.
    """
    try:
        await callback.message.edit_text(
            text=text,
            reply_markup=reply_markup,
        )
        logger.debug(f"Admin message edited for user {callback.from_user.id}")
    except Exception as e:
        logger.warning(f"Failed to edit admin message: {e}")
        # Если не получается отредактировать, отправляем новое
        await callback.message.answer(
            text=text,
            reply_markup=reply_markup,
        )


async def send_admin_message(
    message: Message,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    """
    Отправляет сообщение для админки без изображений.
    """
    try:
        await message.answer(
            text=text,
            reply_markup=reply_markup,
        )
        logger.debug(f"Admin message sent to user {message.from_user.id}")
    except Exception as e:
        logger.error(f"Failed to send admin message: {e}")
