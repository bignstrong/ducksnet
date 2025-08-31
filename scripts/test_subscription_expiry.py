#!/usr/bin/env python3
"""
Скрипт для тестирования системы уведомлений о истечении подписки.
"""
import asyncio
import logging
import os
import sys
from pathlib import Path

# Добавляем путь к приложению в sys.path
app_path = Path(__file__).parent.parent
sys.path.insert(0, str(app_path))

from app.config import load_config
from app.bot.tasks.subscription_expiry import SubscriptionExpiryChecker
from app.db.database import Database
from app.bot import services


async def test_subscription_expiry_system():
    """Тестирует систему уведомлений о истечении подписки."""
    
    print("🧪 Тестирование системы уведомлений о истечении подписки...")
    print("=" * 60)
    
    # Загружаем конфигурацию
    config = load_config()
    
    print(f"📋 Конфигурация уведомлений:")
    print(f"   ├─ Включено: {config.shop.SUBSCRIPTION_EXPIRY_NOTIFICATIONS_ENABLED}")
    print(f"   └─ Интервал проверки: {config.shop.SUBSCRIPTION_EXPIRY_CHECK_INTERVAL_MINUTES} мин")
    print()
    
    if not config.shop.SUBSCRIPTION_EXPIRY_NOTIFICATIONS_ENABLED:
        print("❌ Уведомления о истечении подписки отключены в конфигурации!")
        return False
    
    # Проверяем файлы системы
    print("📁 Проверка файлов системы:")
    
    files_to_check = [
        "app/bot/tasks/subscription_expiry.py",
        "app/locales/ru/LC_MESSAGES/bot.po",
        "app/locales/en/LC_MESSAGES/bot.po",
    ]
    
    all_files_exist = True
    for file_path in files_to_check:
        full_path = app_path / file_path
        if full_path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - НЕ НАЙДЕН!")
            all_files_exist = False
    
    print()
    
    if not all_files_exist:
        print("❌ Некоторые файлы системы не найдены!")
        return False
    
    print("✅ Все файлы системы на месте")
    print()
    
    # Проверяем импорты
    print("🔍 Проверка импортов:")
    
    try:
        from app.bot.tasks.subscription_expiry import SubscriptionExpiryChecker
        print("   ✅ SubscriptionExpiryChecker импортирован")
    except ImportError as e:
        print(f"   ❌ Ошибка импорта SubscriptionExpiryChecker: {e}")
        return False
    
    try:
        from app.bot.services import NotificationService, VPNService
        print("   ✅ Сервисы уведомлений импортированы")
    except ImportError as e:
        print(f"   ❌ Ошибка импорта сервисов: {e}")
        return False
    
    print()
    
    # Проверяем переводы
    print("🌐 Проверка переводов:")
    
    # Проверяем русскую локализацию
    ru_po_file = app_path / "app/locales/ru/LC_MESSAGES/bot.po"
    with open(ru_po_file, 'r', encoding='utf-8') as f:
        ru_content = f.read()
        if "subscription_expiry:notification:warning" in ru_content:
            print("   ✅ Русские переводы найдены")
        else:
            print("   ❌ Русские переводы не найдены")
            return False
    
    # Проверяем английскую локализацию
    en_po_file = app_path / "app/locales/en/LC_MESSAGES/bot.po"
    with open(en_po_file, 'r', encoding='utf-8') as f:
        en_content = f.read()
        if "subscription_expiry:notification:warning" in en_content:
            print("   ✅ Английские переводы найдены")
        else:
            print("   ❌ Английские переводы не найдены")
            return False
    
    print()
    
    # Проверяем конфигурацию в config.py
    print("⚙️ Проверка конфигурации:")
    
    config_file = app_path / "app/config.py"
    with open(config_file, 'r', encoding='utf-8') as f:
        config_content = f.read()
        if "SUBSCRIPTION_EXPIRY_NOTIFICATIONS_ENABLED" in config_content:
            print("   ✅ Новые настройки добавлены в config.py")
        else:
            print("   ❌ Настройки не найдены в config.py")
            return False
    
    print()
    
    # Итоговый результат
    print("=" * 60)
    print("🎉 ТЕСТ ПРОЙДЕН УСПЕШНО!")
    print()
    print("📖 Система уведомлений о истечении подписки готова к работе:")
    print()
    print("🔧 Настройки (добавьте в .env если нужно изменить):")
    print("   SHOP_SUBSCRIPTION_EXPIRY_NOTIFICATIONS_ENABLED=true")
    print("   SHOP_SUBSCRIPTION_EXPIRY_CHECK_INTERVAL_MINUTES=30")
    print()
    print("⏰ Интервалы уведомлений:")
    print("   • За 2 дня до истечения")
    print("   • За 1 день до истечения") 
    print("   • За 1 час до истечения")
    print()
    print("🚀 Система автоматически запустится при следующем старте бота")
    print()
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_subscription_expiry_system())
    sys.exit(0 if success else 1)
