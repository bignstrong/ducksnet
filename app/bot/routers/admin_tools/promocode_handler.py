import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters import IsAdmin
from app.bot.models import ServicesContainer
from app.bot.routers.misc.keyboard import back_keyboard
from app.bot.utils.constants import INPUT_PROMOCODE_KEY, MAIN_MESSAGE_ID_KEY
from app.bot.utils.formatting import format_subscription_period
from app.bot.utils.navigation import NavAdminTools
from app.bot.utils.admin_messaging import edit_admin_message, edit_admin_message_by_id
from app.db.models import Promocode, User

from .keyboard import promocode_duration_keyboard, promocode_editor_keyboard

logger = logging.getLogger(__name__)
router = Router(name=__name__)


class CreatePromocodeStates(StatesGroup):
    selecting_duration = State()


class DeletePromocodeStates(StatesGroup):
    promocode_input = State()


class EditPromocodeStates(StatesGroup):
    promocode_input = State()
    selecting_duration = State()


async def show_promocode_editor_main(message: Message, state: FSMContext) -> None:
    await state.set_state(None)
    main_message_id = await state.get_value(MAIN_MESSAGE_ID_KEY)
    await edit_admin_message_by_id(
        message=message,
        message_id=main_message_id,
        text=_("promocode_editor:message:main"),
        reply_markup=promocode_editor_keyboard(),
    )


@router.callback_query(F.data == NavAdminTools.PROMOCODE_EDITOR, IsAdmin())
async def callback_promocode_editor(callback: CallbackQuery, user: User, state: FSMContext) -> None:
    logger.info(f"Admin {user.tg_id} opened promocode editor.")
    await state.clear()  # Clear any active states
    await edit_admin_message(
        callback=callback,
        text=_("promocode_editor:message:main"),
        reply_markup=promocode_editor_keyboard(),
    )


# region: Create Promocode
@router.callback_query(F.data == NavAdminTools.CREATE_PROMOCODE, IsAdmin())
async def callback_create_promocode(callback: CallbackQuery, user: User, state: FSMContext) -> None:
    logger.info(f"Admin {user.tg_id} started creating promocode.")
    await state.set_state(CreatePromocodeStates.selecting_duration)
    await edit_admin_message(
        callback=callback,
        text=_("promocode_editor:message:create"),
        reply_markup=promocode_duration_keyboard(),
    )


@router.callback_query(CreatePromocodeStates.selecting_duration, F.data.regexp(r'^\d+$'), IsAdmin())
async def callback_duration_selected(
    callback: CallbackQuery,
    user: User,
    session: AsyncSession,
    state: FSMContext,
    services: ServicesContainer,
) -> None:
    logger.info(f"Admin {user.tg_id} selected {callback.data} days for promocode.")
    promocode = await Promocode.create(session=session, duration=int(callback.data))
    
    if promocode:
        # Показываем успешное создание в основном сообщении
        await edit_admin_message(
            callback=callback,
            text=_("promocode_editor:message:main") + "\n\n✅ " + _("promocode_editor:ntf:created_success").format(
                promocode=promocode.code,
                duration=format_subscription_period(promocode.duration),
            ),
            reply_markup=promocode_editor_keyboard(),
        )
    else:
        # Показываем ошибку в основном сообщении
        await edit_admin_message(
            callback=callback,
            text=_("promocode_editor:message:main") + "\n\n❌ " + _("promocode_editor:ntf:create_failed"),
            reply_markup=promocode_editor_keyboard(),
        )
    
    await state.set_state(None)


# endregion


# region: Delete Promocode
@router.callback_query(F.data == NavAdminTools.DELETE_PROMOCODE, IsAdmin())
async def callback_delete_promocode(callback: CallbackQuery, user: User, state: FSMContext) -> None:
    logger.info(f"Admin {user.tg_id} started deleting promocode.")
    await state.set_state(DeletePromocodeStates.promocode_input)
    await edit_admin_message(
        callback=callback,
        text=_("promocode_editor:message:delete"),
        reply_markup=back_keyboard(NavAdminTools.PROMOCODE_EDITOR),
    )


@router.message(DeletePromocodeStates.promocode_input, IsAdmin())
async def handle_promocode_input(
    message: Message,
    user: User,
    session: AsyncSession,
    state: FSMContext,
    services: ServicesContainer,
) -> None:
    input_promocode = message.text.strip()
    logger.info(f"Admin {user.tg_id} entered promocode: {input_promocode} for deleting.")

    main_message_id = await state.get_value(MAIN_MESSAGE_ID_KEY)
    
    if await Promocode.delete(session=session, code=input_promocode):
        # Показываем успешное удаление в основном сообщении
        await edit_admin_message_by_id(
            message=message,
            message_id=main_message_id,
            text=_("promocode_editor:message:main") + "\n\n✅ " + _("promocode_editor:ntf:deleted_success").format(promocode=input_promocode),
            reply_markup=promocode_editor_keyboard(),
        )
    else:
        # Показываем ошибку в основном сообщении
        await edit_admin_message_by_id(
            message=message,
            message_id=main_message_id,
            text=_("promocode_editor:message:main") + "\n\n❌ " + _("promocode_editor:ntf:delete_failed"),
            reply_markup=promocode_editor_keyboard(),
        )
    
    await state.set_state(None)


# endregion


# region Edit Promocode
@router.callback_query(F.data == NavAdminTools.EDIT_PROMOCODE, IsAdmin())
async def callback_edit_promocode(callback: CallbackQuery, user: User, state: FSMContext) -> None:
    logger.info(f"Admin {user.tg_id} started editing promocode.")
    await state.set_state(EditPromocodeStates.promocode_input)
    await edit_admin_message(
        callback=callback,
        text=_("promocode_editor:message:edit"),
        reply_markup=back_keyboard(NavAdminTools.PROMOCODE_EDITOR),
    )


@router.message(EditPromocodeStates.promocode_input, IsAdmin())
async def handle_promocode_input(
    message: Message,
    user: User,
    session: AsyncSession,
    state: FSMContext,
    services: ServicesContainer,
) -> None:
    input_promocode = message.text.strip()
    logger.info(f"Admin {user.tg_id} entered promocode: {input_promocode} for editing.")

    promocode = await Promocode.get(session=session, code=input_promocode)
    if promocode and not promocode.is_activated:
        await state.set_state(EditPromocodeStates.selecting_duration)
        await state.update_data({INPUT_PROMOCODE_KEY: input_promocode})
        main_message_id = await state.get_value(MAIN_MESSAGE_ID_KEY)
        await edit_admin_message_by_id(
            message=message,
            message_id=main_message_id,
            text=_("promocode_editor:message:edit_duration").format(
                promocode=promocode.code,
                duration=promocode.duration,
            ),
            reply_markup=promocode_duration_keyboard(),
        )
    else:
        # Показываем ошибку в основном сообщении
        main_message_id = await state.get_value(MAIN_MESSAGE_ID_KEY)
        await edit_admin_message_by_id(
            message=message,
            message_id=main_message_id,
            text=_("promocode_editor:message:main") + "\n\n❌ " + _("promocode_editor:ntf:edit_failed"),
            reply_markup=promocode_editor_keyboard(),
        )
        await state.set_state(None)


@router.callback_query(EditPromocodeStates.selecting_duration, F.data.regexp(r'^\d+$'), IsAdmin())
async def callback_edit_duration_selected(
    callback: CallbackQuery,
    user: User,
    session: AsyncSession,
    state: FSMContext,
    services: ServicesContainer,
) -> None:
    logger.info(f"Admin {user.tg_id} selected {callback.data} days for promocode edit.")
    input_promocode = await state.get_value(INPUT_PROMOCODE_KEY)
    promocode = await Promocode.update(
        session=session,
        code=input_promocode,
        duration=int(callback.data),
    )
    
    # Показываем успешное редактирование в основном сообщении
    await edit_admin_message(
        callback=callback,
        text=_("promocode_editor:message:main") + "\n\n✅ " + _("promocode_editor:ntf:edited_success").format(
            promocode=promocode.code,
            duration=format_subscription_period(promocode.duration),
        ),
        reply_markup=promocode_editor_keyboard(),
    )
    await state.set_state(None)


# endregion
