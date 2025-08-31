import logging
from datetime import datetime, timedelta, timezone
from typing import Set

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.bot.services import NotificationService, VPNService
from app.config import Config
from app.db.models import User

logger = logging.getLogger(__name__)


class SubscriptionExpiryChecker:
    """
    Сервис для проверки истечения подписок и отправки уведомлений.
    """

    def __init__(
        self,
        session_factory: async_sessionmaker,
        notification_service: NotificationService,
        vpn_service: VPNService,
        config: Config,
    ) -> None:
        self.session_factory = session_factory
        self.notification_service = notification_service
        self.vpn_service = vpn_service
        self.config = config
        self.scheduler = AsyncIOScheduler()
        # Кэш для предотвращения дублирования уведомлений
        # Формат: {user_id}_{interval_hours}
        self.notification_cache: Set[str] = set()

    async def check_expiring_subscriptions(self) -> None:
        """
        Проверяет все подписки пользователей и отправляет уведомления
        за 2 дня, 1 день и 1 час до истечения.
        """
        # Проверяем, включены ли уведомления
        if not self.config.shop.SUBSCRIPTION_EXPIRY_NOTIFICATIONS_ENABLED:
            logger.debug("Subscription expiry notifications are disabled")
            return

        logger.info("Starting subscription expiry check...")

        session: AsyncSession
        async with self.session_factory() as session:
            # Получаем всех пользователей с сервером (активной подпиской)
            query = await session.execute(
                select(User).where(User.server_id.isnot(None))
            )
            users_with_subscription = query.scalars().all()

            logger.info(f"Found {len(users_with_subscription)} users with active subscriptions")

            for user in users_with_subscription:
                try:
                    await self._check_user_subscription(user)
                except Exception as e:
                    logger.error(f"Error checking subscription for user {user.tg_id}: {e}")

        logger.info("Subscription expiry check completed")

    async def _check_user_subscription(self, user: User) -> None:
        """
        Проверяет подписку конкретного пользователя и отправляет уведомления при необходимости.
        """
        try:
            # Получаем данные клиента VPN
            client_data = await self.vpn_service.get_client_data(user)
            
            if not client_data:
                logger.warning(f"Could not get client data for user {user.tg_id}")
                return

            # Проверяем, если подписка уже истекла
            if client_data.has_subscription_expired:
                logger.debug(f"Subscription already expired for user {user.tg_id}")
                return

            # Получаем timestamp истечения подписки
            expiry_timestamp = client_data._expiry_time
            
            if expiry_timestamp == -1:
                # Безлимитная подписка
                logger.debug(f"User {user.tg_id} has unlimited subscription")
                return

            # Конвертируем timestamp в datetime
            expiry_datetime = datetime.fromtimestamp(expiry_timestamp / 1000, tz=timezone.utc)
            current_datetime = datetime.now(timezone.utc)
            
            time_until_expiry = expiry_datetime - current_datetime

            # Проверяем временные интервалы для уведомлений
            await self._send_notification_if_needed(user, time_until_expiry, expiry_datetime)

        except Exception as e:
            logger.error(f"Error processing user {user.tg_id}: {e}")

    async def _send_notification_if_needed(
        self, 
        user: User, 
        time_until_expiry: timedelta, 
        expiry_datetime: datetime
    ) -> None:
        """
        Отправляет уведомление пользователю, если подписка истекает в установленные промежутки времени.
        """
        total_hours = time_until_expiry.total_seconds() / 3600
        
        # Интервалы уведомлений в часах
        notification_intervals = {
            48: "2 дня",  # 48 часов = 2 дня
            24: "1 день",  # 24 часа = 1 день
            1: "1 час"     # 1 час
        }

        for hours, time_description in notification_intervals.items():
            # Проверяем, попадает ли оставшееся время в диапазон уведомления
            # Допускаем погрешность в половину интервала проверки для учета интервала проверки
            check_interval = self.config.shop.SUBSCRIPTION_EXPIRY_CHECK_INTERVAL_MINUTES / 60
            tolerance = check_interval / 2
            
            if hours - tolerance <= total_hours <= hours + tolerance:
                # Проверяем кэш, чтобы не отправлять дублирующие уведомления
                cache_key = f"{user.tg_id}_{hours}"
                if cache_key not in self.notification_cache:
                    await self._send_expiry_notification(user, time_description, expiry_datetime)
                    self.notification_cache.add(cache_key)
                    
                    # Очищаем старые записи из кэша (записи старше 7 дней)
                    await self._cleanup_notification_cache()
                break

    async def _send_expiry_notification(
        self, 
        user: User, 
        time_description: str, 
        expiry_datetime: datetime
    ) -> None:
        """
        Отправляет уведомление о скором истечении подписки.
        """
        try:
            from aiogram.utils.i18n import gettext as _
            
            # Форматируем дату истечения для отображения
            expiry_str = expiry_datetime.strftime("%d.%m.%Y %H:%M UTC")
            
            # Формируем текст уведомления
            notification_text = _(
                "subscription_expiry:notification:warning"
            ).format(
                time_left=time_description,
                expiry_date=expiry_str
            )

            # Отправляем уведомление пользователю
            await self.notification_service.notify_by_id(
                chat_id=user.tg_id,
                text=notification_text,
                duration=0  # Постоянное уведомление
            )

            logger.info(
                f"Sent expiry notification to user {user.tg_id} "
                f"(expires in {time_description})"
            )

        except Exception as e:
            logger.error(
                f"Failed to send expiry notification to user {user.tg_id}: {e}"
            )

    async def _cleanup_notification_cache(self) -> None:
        """
        Простая очистка кэша. В продакшен можно заменить на Redis с TTL.
        """
        # Ограничиваем размер кэша простым способом
        if len(self.notification_cache) > 10000:
            # Очищаем половину самых старых записей
            cache_list = list(self.notification_cache)
            self.notification_cache = set(cache_list[len(cache_list)//2:])
            logger.info("Notification cache cleaned up")

    def start_scheduler(self) -> None:
        """
        Запускает планировщик для периодической проверки истечения подписок.
        Интервал проверки настраивается через конфигурацию.
        """
        if self.scheduler.running:
            logger.warning("Subscription expiry scheduler is already running")
            return

        check_interval = self.config.shop.SUBSCRIPTION_EXPIRY_CHECK_INTERVAL_MINUTES

        # Добавляем задачу в планировщик
        self.scheduler.add_job(
            self.check_expiring_subscriptions,
            trigger="interval",
            minutes=check_interval,
            id="subscription_expiry_check",
            replace_existing=True,
        )

        self.scheduler.start()
        logger.info(f"Subscription expiry scheduler started (every {check_interval} minutes)")

    def stop_scheduler(self) -> None:
        """
        Останавливает планировщик проверки истечения подписок.
        """
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Subscription expiry scheduler stopped")


def start_scheduler(
    session_factory: async_sessionmaker,
    notification_service: NotificationService,
    vpn_service: VPNService,
    config: Config,
) -> SubscriptionExpiryChecker:
    """
    Инициализирует и запускает планировщик проверки истечения подписок.
    """
    checker = SubscriptionExpiryChecker(
        session_factory=session_factory,
        notification_service=notification_service,
        vpn_service=vpn_service,
        config=config,
    )
    checker.start_scheduler()
    return checker
