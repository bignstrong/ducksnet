"""
Клавиатуры для обработки подписки на канал.
"""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder


def subscription_required_keyboard(
    channel_username: str | None = None,
    channel_id: int | str | None = None
) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для неподписанных пользователей.
    
    Args:
        channel_username: Имя пользователя канала (без @)
        channel_id: ID канала или полное имя (@channel)
    """
    builder = InlineKeyboardBuilder()

    # Кнопка для подписки на канал
    if channel_username:
        channel_url = f"https://t.me/{channel_username}"
        builder.row(
            InlineKeyboardButton(
                text=_("subscription_required:button:subscribe"),
                url=channel_url
            )
        )
    elif channel_id and str(channel_id).startswith("@"):
        channel_url = f"https://t.me/{str(channel_id)[1:]}"  # Убираем @
        builder.row(
            InlineKeyboardButton(
                text=_("subscription_required:button:subscribe"),
                url=channel_url
            )
        )

    # Кнопка "Я подписался"
    builder.row(
        InlineKeyboardButton(
            text=_("subscription_required:button:check_subscription"),
            callback_data="check_subscription"
        )
    )

    return builder.as_markup()


def subscription_check_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура с кнопкой повторной проверки подписки.
    """
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=_("subscription_required:button:check_again"),
            callback_data="check_subscription"
        )
    )
    
    return builder.as_markup()
