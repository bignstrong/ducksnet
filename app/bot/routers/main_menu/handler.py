import logging
import os
from pathlib import Path

from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import CallbackQuery, Message, FSInputFile
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters import IsAdmin
from app.bot.models import ServicesContainer
from app.bot.utils.constants import MAIN_MESSAGE_ID_KEY
from app.bot.utils.navigation import NavMain
from app.config import Config, DEFAULT_DATA_DIR
from app.db.models import Invite, Referral, User

from .keyboard import main_menu_keyboard

logger = logging.getLogger(__name__)
router = Router(name=__name__)

# Путь к изображениям
IMAGES_DIR = DEFAULT_DATA_DIR / "images"

def get_main_menu_image_path(config: Config) -> Path:
    """Получает путь к изображению главного меню из конфигурации"""
    return IMAGES_DIR / config.shop.MAIN_MENU_IMAGE_NAME


async def process_invite_attribution(session: AsyncSession, user: User, invite_hash: str) -> bool:
    logger.info(f"Checking invite {invite_hash} for user {user.tg_id}")
    try:
        invite = await Invite.get_by_hash(session=session, hash_code=invite_hash)
        if not invite or not invite.is_active:
            logger.info(f"Invalid or inactive invite hash: {invite_hash}")
            return False

        user.source_invite_name = invite.name
        await session.commit()

        await Invite.increment_clicks(session=session, invite_id=invite.id)

        logger.info(f"User {user.tg_id} attributed to invite {invite.name}")
        return True
    except Exception as exception:
        logger.critical(f"Invite attribution error for user {user.tg_id}: {exception}")
        return False


async def process_creating_referral(session: AsyncSession, user: User, referrer_id: int) -> bool:
    logger.info(f"Assigning user {user.tg_id} as a referred to a referrer user {referrer_id}")
    try:
        referrer = await User.get(session=session, tg_id=referrer_id)
        if not referrer or referrer.tg_id == user.tg_id:
            logger.info(
                f"Failed to assign user {user.tg_id} as a referred to a referrer user {referrer_id}."
                f"Invalid string received."
            )
            return False

        await Referral.create(
            session=session, referrer_tg_id=referrer.tg_id, referred_tg_id=user.tg_id
        )
        logger.info(
            f"User {user.tg_id} assigned as referred to a referrer with tg id {referrer.tg_id}"
        )
        return True
    except Exception as exception:
        logger.critical(
            f"Referral creation error for {user.tg_id} (arg: {referrer_id}): {exception}"
        )
        return False


async def send_main_menu_with_image(
    message: Message,
    text: str,
    reply_markup,
    user_id: int,
    state: FSMContext,
    config: Config,
) -> Message:
    """Отправляет главное меню с изображением, если оно существует"""
    try:
        if config.shop.MAIN_MENU_IMAGE_ENABLED and get_main_menu_image_path(config).exists():
            # Отправляем изображение с подписью
            photo = FSInputFile(get_main_menu_image_path(config))
            main_menu = await message.answer_photo(
                photo=photo,
                caption=text,
                reply_markup=reply_markup,
            )
            logger.debug(f"Main menu with image sent to user {user_id}")
        else:
            # Отправляем только текст, если изображения нет или отключено
            main_menu = await message.answer(
                text=text,
                reply_markup=reply_markup,
            )
            logger.debug(f"Main menu without image sent to user {user_id}")
    except Exception as exception:
        logger.error(f"Failed to send main menu with image to user {user_id}: {exception}")
        # Fallback к отправке только текста
        main_menu = await message.answer(
            text=text,
            reply_markup=reply_markup,
        )

    await state.update_data({MAIN_MESSAGE_ID_KEY: main_menu.message_id})
    return main_menu

async def edit_main_menu_with_image(
    callback: CallbackQuery,
    text: str,
    reply_markup,
    user_id: int,
    state: FSMContext,
    config: Config,
) -> None:
    """Редактирует главное меню с изображением, если оно существует"""
    try:
        if config.shop.MAIN_MENU_IMAGE_ENABLED and get_main_menu_image_path(config).exists():
            # Редактируем сообщение с изображением
            photo = FSInputFile(get_main_menu_image_path(config))
            await callback.message.edit_media(
                media=photo,
                reply_markup=reply_markup,
            )
            await callback.message.edit_caption(
                caption=text,
                reply_markup=reply_markup,
            )
            logger.debug(f"Main menu with image edited for user {user_id}")
        else:
            # Редактируем только текст, если изображения нет или отключено
            await callback.message.edit_text(
                text=text,
                reply_markup=reply_markup,
            )
            logger.debug(f"Main menu without image edited for user {user_id}")
    except Exception as exception:
        logger.error(f"Failed to edit main menu with image for user {user_id}: {exception}")
        # Fallback к редактированию только текста
        await callback.message.edit_text(
            text=text,
            reply_markup=reply_markup,
        )


@router.message(Command(NavMain.START))
async def command_main_menu(
    message: Message,
    user: User,
    state: FSMContext,
    services: ServicesContainer,
    config: Config,
    session: AsyncSession,
    command: CommandObject,
    is_new_user: bool,
) -> None:
    logger.info(f"User {user.tg_id} opened main menu page.")
    previous_message_id = await state.get_value(MAIN_MESSAGE_ID_KEY)

    if previous_message_id:
        try:
            await message.bot.delete_message(chat_id=user.tg_id, message_id=previous_message_id)
            logger.debug(f"Main message for user {user.tg_id} deleted.")
        except Exception as exception:
            logger.error(f"Failed to delete main message for user {user.tg_id}: {exception}")
        finally:
            await state.clear()

    if command.args and is_new_user:
        if command.args.isdigit():
            await process_creating_referral(
                session=session, user=user, referrer_id=int(command.args)
            )
        else:
            await process_invite_attribution(session=session, user=user, invite_hash=command.args)

    is_admin = await IsAdmin()(user_id=user.tg_id)
    main_menu = await send_main_menu_with_image(
        message=message,
        text=_("main_menu:message:main").format(name=user.first_name),
        reply_markup=main_menu_keyboard(
            is_admin,
            is_referral_available=config.shop.REFERRER_REWARD_ENABLED,
            is_trial_available=await services.subscription.is_trial_available(user),
            is_referred_trial_available=await services.referral.is_referred_trial_available(user),
        ),
        user_id=user.tg_id,
        state=state,
        config=config,
    )


@router.callback_query(F.data == NavMain.MAIN_MENU)
async def callback_main_menu(
    callback: CallbackQuery,
    user: User,
    services: ServicesContainer,
    state: FSMContext,
    config: Config,
) -> None:
    logger.info(f"User {user.tg_id} returned to main menu page.")
    await state.clear()
    await state.update_data({MAIN_MESSAGE_ID_KEY: callback.message.message_id})
    is_admin = await IsAdmin()(user_id=user.tg_id)
    await edit_main_menu_with_image(
        callback=callback,
        text=_("main_menu:message:main").format(name=user.first_name),
        reply_markup=main_menu_keyboard(
            is_admin,
            is_referral_available=config.shop.REFERRER_REWARD_ENABLED,
            is_trial_available=await services.subscription.is_trial_available(user),
            is_referred_trial_available=await services.referral.is_referred_trial_available(user),
        ),
        user_id=user.tg_id,
        state=state,
        config=config,
    )


async def redirect_to_main_menu(
    bot: Bot,
    user: User,
    services: ServicesContainer,
    config: Config,
    storage: RedisStorage | None = None,
    state: FSMContext | None = None,
) -> None:
    logger.info(f"User {user.tg_id} redirected to main menu page.")

    if not state:
        state: FSMContext = FSMContext(
            storage=storage,
            key=StorageKey(bot_id=bot.id, chat_id=user.tg_id, user_id=user.tg_id),
        )

    main_message_id = await state.get_value(MAIN_MESSAGE_ID_KEY)
    is_admin = await IsAdmin()(user_id=user.tg_id)

    try:
        if config.shop.MAIN_MENU_IMAGE_ENABLED and get_main_menu_image_path(config).exists():
            # Редактируем сообщение с изображением
            photo = FSInputFile(get_main_menu_image_path(config))
            await bot.edit_message_media(
                media=photo,
                chat_id=user.tg_id,
                message_id=main_message_id,
                reply_markup=main_menu_keyboard(
                    is_admin,
                    is_referral_available=config.shop.REFERRER_REWARD_ENABLED,
                    is_trial_available=await services.subscription.is_trial_available(user),
                    is_referred_trial_available=await services.referral.is_referred_trial_available(
                        user
                    ),
                ),
            )
            await bot.edit_message_caption(
                caption=_("main_menu:message:main").format(name=user.first_name),
                chat_id=user.tg_id,
                message_id=main_message_id,
                reply_markup=main_menu_keyboard(
                    is_admin,
                    is_referral_available=config.shop.REFERRER_REWARD_ENABLED,
                    is_trial_available=await services.subscription.is_trial_available(user),
                    is_referred_trial_available=await services.referral.is_referred_trial_available(
                        user
                    ),
                ),
            )
        else:
            # Редактируем только текст, если изображения нет или отключено
            await bot.edit_message_text(
                text=_("main_menu:message:main").format(name=user.first_name),
                chat_id=user.tg_id,
                message_id=main_message_id,
                reply_markup=main_menu_keyboard(
                    is_admin,
                    is_referral_available=config.shop.REFERRER_REWARD_ENABLED,
                    is_trial_available=await services.subscription.is_trial_available(user),
                    is_referred_trial_available=await services.referral.is_referred_trial_available(
                        user
                    ),
                ),
            )
    except Exception as exception:
        logger.error(f"Error redirecting to main menu page: {exception}")
