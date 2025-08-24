import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsAdmin, IsDev
from app.bot.utils.navigation import NavAdminTools
from app.db.models import User

from .keyboard import admin_tools_keyboard

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(F.data == NavAdminTools.MAIN, IsAdmin())
async def callback_admin_tools_main(callback: CallbackQuery, user: User) -> None:
    logger.info(f"Admin {user.tg_id} opened admin tools.")
    is_dev = await IsDev()(user_id=user.tg_id)
    
    try:
        await callback.message.edit_text(
            text=_("admin_tools:message:main"),
            reply_markup=admin_tools_keyboard(is_dev),
        )
    except Exception as e:
        logger.warning(f"Failed to edit admin message, sending new: {e}")
        await callback.message.answer(
            text=_("admin_tools:message:main"),
            reply_markup=admin_tools_keyboard(is_dev),
        )
