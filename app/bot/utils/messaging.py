"""
Утилиты для отправки сообщений с изображением главного меню.
"""
import logging
from pathlib import Path
from typing import Optional, Union

from aiogram import Bot
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
)

from app.config import Config, DEFAULT_DATA_DIR

logger = logging.getLogger(__name__)

# Путь к изображениям
IMAGES_DIR = DEFAULT_DATA_DIR / "images"


def get_main_menu_image_path(config: Config) -> Path:
    """Получает путь к изображению главного меню из конфигурации"""
    return IMAGES_DIR / config.shop.MAIN_MENU_IMAGE_NAME


async def send_message_with_image(
    bot: Bot,
    chat_id: int,
    text: str,
    config: Config,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
    **kwargs
) -> Message:
    """
    Отправляет сообщение с изображением, если оно включено и существует.
    Иначе отправляет только текст.
    """
    try:
        if config.shop.MAIN_MENU_IMAGE_ENABLED and get_main_menu_image_path(config).exists():
            # Отправляем изображение с подписью
            photo = FSInputFile(get_main_menu_image_path(config))
            message = await bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=text,
                reply_markup=reply_markup,
                **kwargs
            )
            logger.debug(f"Message with image sent to chat {chat_id}")
        else:
            # Отправляем только текст, если изображения нет или отключено
            message = await bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=reply_markup,
                **kwargs
            )
            logger.debug(f"Text message sent to chat {chat_id}")
    except Exception as exception:
        logger.error(f"Failed to send message with image to chat {chat_id}: {exception}")
        # Fallback к отправке только текста
        message = await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
            **kwargs
        )

    return message


async def answer_with_image(
    message: Message,
    text: str,
    config: Config,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
    **kwargs
) -> Message:
    """
    Отвечает на сообщение с изображением, если оно включено и существует.
    Иначе отвечает только текстом.
    """
    return await send_message_with_image(
        bot=message.bot,
        chat_id=message.chat.id,
        text=text,
        config=config,
        reply_markup=reply_markup,
        **kwargs
    )


async def edit_message_with_image(
    bot: Bot,
    chat_id: int,
    message_id: int,
    text: str,
    config: Config,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
    **kwargs
) -> bool:
    """
    Редактирует сообщение с изображением, если оно включено и существует.
    Иначе редактирует только текст.
    """
    try:
        if config.shop.MAIN_MENU_IMAGE_ENABLED and get_main_menu_image_path(config).exists():
            # Попытка редактировать как медиа с подписью
            try:
                photo = FSInputFile(get_main_menu_image_path(config))
                media = InputMediaPhoto(media=photo, caption=text)
                await bot.edit_message_media(
                    chat_id=chat_id,
                    message_id=message_id,
                    media=media,
                    reply_markup=reply_markup,
                    **kwargs
                )
                logger.debug(f"Message with image edited in chat {chat_id}")
                return True
            except Exception as media_exception:
                logger.warning(f"Failed to edit as media, trying caption edit: {media_exception}")
                # Попытка редактировать только подпись
                await bot.edit_message_caption(
                    chat_id=chat_id,
                    message_id=message_id,
                    caption=text,
                    reply_markup=reply_markup,
                    **kwargs
                )
                logger.debug(f"Message caption edited in chat {chat_id}")
                return True
        else:
            # Редактируем только текст, если изображения нет или отключено
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                reply_markup=reply_markup,
                **kwargs
            )
            logger.debug(f"Text message edited in chat {chat_id}")
            return True
    except Exception as exception:
        logger.error(f"Failed to edit message with image in chat {chat_id}: {exception}")
        return False


async def edit_callback_with_image(
    callback: CallbackQuery,
    text: str,
    config: Config,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
    **kwargs
) -> bool:
    """
    Редактирует сообщение callback query с изображением, если оно включено и существует.
    Иначе редактирует только текст.
    """
    if not callback.message:
        return False
        
    return await edit_message_with_image(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text=text,
        config=config,
        reply_markup=reply_markup,
        **kwargs
    )


# Вспомогательные методы для совместимости с существующим кодом
class MessageWithImage:
    """Обертка для сообщений с поддержкой изображений"""
    
    def __init__(self, message: Message, config: Config):
        self.message = message
        self.config = config
        self.bot = message.bot
        self.chat = message.chat
    
    async def answer(
        self,
        text: str,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
        **kwargs
    ) -> Message:
        """Отвечает с изображением"""
        return await answer_with_image(
            message=self.message,
            text=text,
            config=self.config,
            reply_markup=reply_markup,
            **kwargs
        )
    
    async def edit_text(
        self,
        text: str,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
        **kwargs
    ) -> bool:
        """Редактирует текст с изображением"""
        return await edit_message_with_image(
            bot=self.bot,
            chat_id=self.chat.id,
            message_id=self.message.message_id,
            text=text,
            config=self.config,
            reply_markup=reply_markup,
            **kwargs
        )


class CallbackWithImage:
    """Обертка для callback query с поддержкой изображений"""
    
    def __init__(self, callback: CallbackQuery, config: Config):
        self.callback = callback
        self.config = config
        self.message = callback.message
        self.bot = callback.bot
    
    async def edit_text(
        self,
        text: str,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
        **kwargs
    ) -> bool:
        """Редактирует текст с изображением"""
        return await edit_callback_with_image(
            callback=self.callback,
            text=text,
            config=self.config,
            reply_markup=reply_markup,
            **kwargs
        )
    
    async def answer(
        self,
        text: str = None,
        show_alert: bool = False,
        **kwargs
    ):
        """Отвечает на callback query"""
        return await self.callback.answer(text=text, show_alert=show_alert, **kwargs)
