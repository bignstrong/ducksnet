from aiogram import Dispatcher

from .is_admin import IsAdmin
from .is_dev import IsDev
from .is_private import IsPrivate
from .is_subscribed import IsSubscribed, NotSubscribed


def register(dispatcher: Dispatcher, developer_id: int, admins_ids: list[int]) -> None:
    dispatcher.update.filter(IsPrivate())
    IsDev.set_developer(developer_id)
    IsAdmin.set_admins(admins_ids)
