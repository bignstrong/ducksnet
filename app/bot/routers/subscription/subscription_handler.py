import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters import IsSubscribed
from app.bot.models import ClientData, ServicesContainer, SubscriptionData
from app.bot.payment_gateways import GatewayFactory
from app.bot.utils.navigation import NavSubscription
from app.config import Config
from app.db.models import User

from .keyboard import (
    devices_keyboard,
    duration_keyboard,
    payment_method_keyboard,
    subscription_keyboard,
)

logger = logging.getLogger(__name__)
router = Router(name=__name__)


async def show_subscription(
    callback: CallbackQuery,
    client_data: ClientData | None,
    callback_data: SubscriptionData,
    config,  # Добавляем config
) -> None:
    if client_data:
        if client_data.has_subscription_expired:
            text = _("subscription:message:expired")
        else:
            text = _("subscription:message:active").format(
                devices=client_data.max_devices,
                expiry_time=client_data.expiry_time,
            )
    else:
        text = _("subscription:message:not_active")

    from app.bot.utils.messaging import edit_callback_with_image

    await edit_callback_with_image(
        callback=callback,
        text=text,
        config=config,
        reply_markup=subscription_keyboard(
            has_subscription=client_data,
            callback_data=callback_data,
        ),
    )


@router.callback_query(F.data == NavSubscription.MAIN, IsSubscribed())
async def callback_subscription(
    callback: CallbackQuery,
    user: User,
    state: FSMContext,
    services: ServicesContainer,
    config: Config,  # Добавляем config
) -> None:
    logger.info(f"User {user.tg_id} opened subscription page.")
    await state.set_state(None)

    client_data = None
    if user.server_id:
        client_data = await services.vpn.get_client_data(user)
        if not client_data:
            await services.notification.show_popup(
                callback=callback,
                text=_("subscription:popup:error_fetching_data"),
            )
            return

    callback_data = SubscriptionData(state=NavSubscription.PROCESS, user_id=user.tg_id)
    await show_subscription(callback=callback, client_data=client_data, callback_data=callback_data, config=config)


@router.callback_query(SubscriptionData.filter(F.state == NavSubscription.EXTEND), IsSubscribed())
async def callback_subscription_extend(
    callback: CallbackQuery,
    user: User,
    callback_data: SubscriptionData,
    config: Config,
    services: ServicesContainer,
) -> None:
    logger.info(f"User {user.tg_id} started extend subscription.")
    client = await services.vpn.is_client_exists(user)

    current_devices = await services.vpn.get_limit_ip(user=user, client=client)
    if not services.plan.get_plan(current_devices):
        await services.notification.show_popup(
            callback=callback,
            text=_("subscription:popup:error_fetching_plan"),
        )
        return

    callback_data.devices = current_devices
    callback_data.state = NavSubscription.DURATION
    callback_data.is_extend = True
    
    from app.bot.utils.messaging import edit_callback_with_image
    
    await edit_callback_with_image(
        callback=callback,
        text=_("subscription:message:duration"),
        config=config,
        reply_markup=duration_keyboard(
            plan_service=services.plan,
            callback_data=callback_data,
            currency=config.shop.CURRENCY,
        ),
    )


@router.callback_query(SubscriptionData.filter(F.state == NavSubscription.CHANGE), IsSubscribed())
async def callback_subscription_change(
    callback: CallbackQuery,
    user: User,
    callback_data: SubscriptionData,
    services: ServicesContainer,
    config: Config,  # Добавляем config
) -> None:
    logger.info(f"User {user.tg_id} started change subscription.")
    callback_data.state = NavSubscription.DEVICES
    callback_data.is_change = True
    
    from app.bot.utils.messaging import edit_callback_with_image
    
    await edit_callback_with_image(
        callback=callback,
        text=_("subscription:message:devices"),
        config=config,
        reply_markup=devices_keyboard(services.plan.get_all_plans(), callback_data),
    )


@router.callback_query(SubscriptionData.filter(F.state == NavSubscription.PROCESS), IsSubscribed())
async def callback_subscription_process(
    callback: CallbackQuery,
    user: User,
    session: AsyncSession,
    callback_data: SubscriptionData,
    services: ServicesContainer,
    config: Config,  # Добавляем config
) -> None:
    logger.info(f"User {user.tg_id} started subscription process.")
    server = await services.server_pool.get_available_server()

    if not server:
        await services.notification.show_popup(
            callback=callback,
            text=_("subscription:popup:no_available_servers"),
            cache_time=120,
        )
        return

    callback_data.state = NavSubscription.DEVICES
    
    from app.bot.utils.messaging import edit_callback_with_image
    
    await edit_callback_with_image(
        callback=callback,
        text=_("subscription:message:devices"),
        config=config,
        reply_markup=devices_keyboard(services.plan.get_all_plans(), callback_data),
    )


@router.callback_query(SubscriptionData.filter(F.state == NavSubscription.DEVICES), IsSubscribed())
async def callback_devices_selected(
    callback: CallbackQuery,
    user: User,
    callback_data: SubscriptionData,
    config: Config,
    services: ServicesContainer,
) -> None:
    logger.info(f"User {user.tg_id} selected devices: {callback_data.devices}")
    callback_data.state = NavSubscription.DURATION
    
    from app.bot.utils.messaging import edit_callback_with_image
    
    await edit_callback_with_image(
        callback=callback,
        text=_("subscription:message:duration"),
        config=config,
        reply_markup=duration_keyboard(
            plan_service=services.plan,
            callback_data=callback_data,
            currency=config.shop.CURRENCY,
        ),
    )


@router.callback_query(SubscriptionData.filter(F.state == NavSubscription.DURATION), IsSubscribed())
async def callback_duration_selected(
    callback: CallbackQuery,
    user: User,
    callback_data: SubscriptionData,
    services: ServicesContainer,
    gateway_factory: GatewayFactory,
    config: Config,  # Добавляем config
) -> None:
    logger.info(f"User {user.tg_id} selected duration: {callback_data.duration}")
    callback_data.state = NavSubscription.PAY
    
    from app.bot.utils.messaging import edit_callback_with_image
    
    await edit_callback_with_image(
        callback=callback,
        text=_("subscription:message:payment_method"),
        config=config,
        reply_markup=payment_method_keyboard(
            plan=services.plan.get_plan(callback_data.devices),
            callback_data=callback_data,
            gateways=gateway_factory.get_gateways(),
        ),
    )
