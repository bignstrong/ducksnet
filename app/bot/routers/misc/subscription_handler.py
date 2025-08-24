"""
Обработчик для пользователей без подписки на канал.
"""
import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _

from app.bot.filters import NotSubscribed, IsSubscribed
from app.bot.models import ServicesContainer
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
    services: ServicesContainer,  # Получаем services из middleware
) -> None:
    """
    Обработчик для успешной проверки подписки.
    """
    logger.info(f"User {user.tg_id} successfully verified subscription")
    
    # Используем стандартные утилиты для перехода в главное меню
    from app.bot.utils.messaging import edit_callback_with_image
    from app.bot.routers.main_menu.keyboard import main_menu_keyboard
    from app.bot.filters import IsAdmin
    
    # Проверяем права администратора
    is_admin = await IsAdmin()(user_id=user.tg_id)
    
    await edit_callback_with_image(
        callback=callback,
        text=_("main_menu:message:main").format(name=user.first_name),
        config=config,
        reply_markup=main_menu_keyboard(
            is_admin,
            is_referral_available=config.shop.REFERRER_REWARD_ENABLED,
            is_trial_available=await services.subscription.is_trial_available(user),
            is_referred_trial_available=await services.referral.is_referred_trial_available(user),
        ),
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
