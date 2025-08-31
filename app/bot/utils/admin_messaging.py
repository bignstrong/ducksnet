"""
Утилиты для отправки сообщений в админ-панели с изображением.
"""
import logging
from typing import Optional

from aiogram.types import CallbackQuery, FSInputFile, InlineKeyboardMarkup, InputMediaPhoto, Message

from app.config import DEFAULT_DATA_DIR

logger = logging.getLogger(__name__)

# Путь к картинке админ-панели
ADMIN_IMAGE_PATH = DEFAULT_DATA_DIR / "images" / "AdminPanel.png"


async def edit_admin_message(
    callback: CallbackQuery,
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
) -> None:
    """
    Безопасно редактирует сообщение в админ-панели с картинкой.
    
    Args:
        callback: CallbackQuery object
        text: Текст сообщения (будет использован как caption)
        reply_markup: Клавиатура
    """
    try:
        # Пытаемся заменить картинку и текст
        if ADMIN_IMAGE_PATH.exists():
            photo = FSInputFile(ADMIN_IMAGE_PATH)
            media = InputMediaPhoto(
                media=photo, 
                caption=text
            )
            await callback.message.edit_media(
                media=media,
                reply_markup=reply_markup,
            )
            logger.debug(f"Admin message with image edited in chat {callback.message.chat.id}")
        else:
            # Если картинки нет, редактируем только подпись
            await callback.message.edit_caption(
                caption=text,
                reply_markup=reply_markup,
            )
            logger.debug(f"Admin message caption edited in chat {callback.message.chat.id}")
    except Exception as e:
        logger.warning(f"Failed to edit admin message: {e}")
        # Fallback - отправляем новое сообщение
        try:
            if ADMIN_IMAGE_PATH.exists():
                photo = FSInputFile(ADMIN_IMAGE_PATH)
                await callback.message.answer_photo(
                    photo=photo,
                    caption=text,
                    reply_markup=reply_markup,
                )
                logger.debug(f"New admin message with image sent to chat {callback.message.chat.id}")
            else:
                await callback.message.answer(
                    text=text,
                    reply_markup=reply_markup,
                )
                logger.debug(f"New admin text message sent to chat {callback.message.chat.id}")
        except Exception as fallback_error:
            logger.error(f"Failed to send fallback admin message: {fallback_error}")


async def send_admin_message(
    message: Message,
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
) -> None:
    """
    Отправляет новое сообщение в админ-панели с картинкой.
    
    Args:
        message: Message object
        text: Текст сообщения (будет использован как caption)
        reply_markup: Клавиатура
    """
    try:
        if ADMIN_IMAGE_PATH.exists():
            photo = FSInputFile(ADMIN_IMAGE_PATH)
            await message.answer_photo(
                photo=photo,
                caption=text,
                reply_markup=reply_markup,
            )
            logger.debug(f"Admin message with image sent to chat {message.chat.id}")
        else:
            await message.answer(
                text=text,
                reply_markup=reply_markup,
            )
            logger.debug(f"Admin text message sent to chat {message.chat.id}")
    except Exception as e:
        logger.error(f"Failed to send admin message: {e}")


async def edit_admin_message_by_id(
    message: Message,
    message_id: int,
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
) -> None:
    """
    Безопасно редактирует сообщение админ-панели по ID с картинкой.
    
    Args:
        message: Message object для получения бота и чата
        message_id: ID сообщения для редактирования
        text: Текст сообщения (будет использован как caption)
        reply_markup: Клавиатура
    """
    try:
        # Пытаемся заменить картинку и текст
        if ADMIN_IMAGE_PATH.exists():
            photo = FSInputFile(ADMIN_IMAGE_PATH)
            media = InputMediaPhoto(
                media=photo, 
                caption=text
            )
            await message.bot.edit_message_media(
                chat_id=message.chat.id,
                message_id=message_id,
                media=media,
                reply_markup=reply_markup,
            )
            logger.debug(f"Admin message with image edited by ID {message_id} in chat {message.chat.id}")
        else:
            # Если картинки нет, редактируем только подпись
            await message.bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=message_id,
                caption=text,
                reply_markup=reply_markup,
            )
            logger.debug(f"Admin message caption edited by ID {message_id} in chat {message.chat.id}")
    except Exception as e:
        logger.warning(f"Failed to edit admin message by ID {message_id}: {e}")
        # Fallback - отправляем новое сообщение
        try:
            if ADMIN_IMAGE_PATH.exists():
                photo = FSInputFile(ADMIN_IMAGE_PATH)
                await message.answer_photo(
                    photo=photo,
                    caption=text,
                    reply_markup=reply_markup,
                )
                logger.debug(f"New admin message with image sent to chat {message.chat.id} (fallback)")
            else:
                await message.answer(
                    text=text,
                    reply_markup=reply_markup,
                )
                logger.debug(f"New admin text message sent to chat {message.chat.id} (fallback)")
        except Exception as fallback_error:
            logger.error(f"Failed to send fallback admin message: {fallback_error}")
