"""
Обработчик для пользователей без подписки на канал.
"""
import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _

from app.bot.filters import NotSubscribed, IsSubscribed
from app.bot.utils.messaging import answer_with_image, edit_callback_with_image
from app.config import Config
from app.db.models import User

from .subscription_keyboard import subscription_required_keyboard, subscription_check_keyboard

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.message(NotSubscribed())
async def handle_not_subscribed_message(
    message: Message,
    user: User,
    config: Config,
    channel_id: int | str | None = None,
    channel_username: str | None = None,
    **kwargs
) -> None:
    """
    Обработчик для сообщений от неподписанных пользователей.
    """
    logger.info(f"Blocking user {user.tg_id} - not subscribed to channel")
    
    await answer_with_image(
        message=message,
        text=_("subscription_required:message:not_subscribed"),
        config=config,
        reply_markup=subscription_required_keyboard(
            channel_username=channel_username,
            channel_id=channel_id
        ),
    )


@router.callback_query(NotSubscribed())
async def handle_not_subscribed_callback(
    callback: CallbackQuery,
    user: User,
    config: Config,
    channel_id: int | str | None = None,
    channel_username: str | None = None,
    **kwargs
) -> None:
    """
    Обработчик для callback query от неподписанных пользователей.
    """
    logger.info(f"Blocking user {user.tg_id} callback - not subscribed to channel")
    
    await edit_callback_with_image(
        callback=callback,
        text=_("subscription_required:message:not_subscribed"),
        config=config,
        reply_markup=subscription_required_keyboard(
            channel_username=channel_username,
            channel_id=channel_id
        ),
    )


@router.callback_query(F.data == "check_subscription", IsSubscribed())
async def handle_subscription_check_success(
    callback: CallbackQuery,
    user: User,
    config: Config,
) -> None:
    """
    Обработчик для успешной проверки подписки.
    """
    logger.info(f"User {user.tg_id} successfully verified subscription")
    
    # Перенаправляем пользователя в главное меню
    from app.bot.routers.main_menu.handler import redirect_to_main_menu
    from app.bot.models import ServicesContainer
    
    # Получаем services из данных middleware
    services = callback.bot["services"]  # Это нужно будет настроить в main
    
    await redirect_to_main_menu(
        bot=callback.bot,
        user=user,
        services=services,
        config=config,
        state=None,  # Можно получить из FSMContext если нужно
    )


@router.callback_query(F.data == "check_subscription", NotSubscribed())
async def handle_subscription_check_failed(
    callback: CallbackQuery,
    user: User,
    config: Config,
    channel_id: int | str | None = None,
    channel_username: str | None = None,
    **kwargs
) -> None:
    """
    Обработчик для неудачной проверки подписки.
    """
    logger.info(f"User {user.tg_id} still not subscribed after check")
    
    await edit_callback_with_image(
        callback=callback,
        text=_("subscription_required:message:still_not_subscribed"),
        config=config,
        reply_markup=subscription_required_keyboard(
            channel_username=channel_username,
            channel_id=channel_id
        ),
    )
    
    # Показываем уведомление
    await callback.answer(
        text=_("subscription_required:popup:still_not_subscribed"),
        show_alert=True
    )
