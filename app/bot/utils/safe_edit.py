"""
Utility for safe message editing.
"""
import logging
from typing import Optional

from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from aiogram.exceptions import TelegramBadRequest

logger = logging.getLogger(__name__)


async def safe_edit_text(
    callback: CallbackQuery,
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
) -> None:
    """
    Safely edit message text or send new message if editing fails.
    
    Args:
        callback: CallbackQuery object
        text: Message text
        reply_markup: Optional inline keyboard
    """
    try:
        await callback.message.edit_text(
            text=text,
            reply_markup=reply_markup,
        )
    except TelegramBadRequest as e:
        if "there is no text in the message to edit" in str(e):
            logger.warning(f"Cannot edit message without text, sending new one")
            await callback.message.answer(
                text=text,
                reply_markup=reply_markup,
            )
        else:
            # Re-raise other telegram errors
            raise
    except Exception as e:
        logger.warning(f"Failed to edit message, sending new one: {e}")
        await callback.message.answer(
            text=text,
            reply_markup=reply_markup,
        )
