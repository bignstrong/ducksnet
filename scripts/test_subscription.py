#!/usr/bin/env python3
"""
Скрипт для тестирования системы принудительной подписки на канал.
"""
import asyncio
import os
import sys
from pathlib import Path

# Добавляем путь к приложению в sys.path
app_path = Path(__file__).parent.parent
sys.path.insert(0, str(app_path))

from app.config import load_config


async def test_subscription_system():
    """Тестирует систему проверки подписки."""
    
    print("🧪 Тестирование системы принудительной подписки на канал...")
    print("=" * 60)
    
    # Загружаем конфигурацию
    config = load_config()
    
    print(f"📋 Конфигурация подписки:")
    print(f"   ├─ Включено: {config.shop.FORCE_SUBSCRIPTION_ENABLED}")
    print(f"   ├─ ID канала: {config.shop.FORCE_SUBSCRIPTION_CHANNEL_ID}")
    print(f"   └─ Username канала: @{config.shop.FORCE_SUBSCRIPTION_CHANNEL_USERNAME}")
    print()
    
    if not config.shop.FORCE_SUBSCRIPTION_ENABLED:
        print("❌ Принудительная подписка отключена в конфигурации!")
        return False
    
    if not config.shop.FORCE_SUBSCRIPTION_CHANNEL_ID and not config.shop.FORCE_SUBSCRIPTION_CHANNEL_USERNAME:
        print("❌ Не настроен канал для проверки подписки!")
        return False
    
    print("✅ Базовая конфигурация корректна")
    print()
    
    # Проверяем файлы системы
    print("📁 Проверка файлов системы:")
    
    files_to_check = [
        ("app/bot/filters/is_subscribed.py", "Фильтры подписки"),
        ("app/bot/routers/misc/subscription_handler.py", "Обработчик подписки"),
        ("app/bot/routers/misc/subscription_keyboard.py", "Клавиатуры подписки"),
        ("app/locales/ru/LC_MESSAGES/bot.po", "Русская локализация"),
        ("app/locales/en/LC_MESSAGES/bot.po", "Английская локализация"),
    ]
    
    all_files_exist = True
    for file_path, description in files_to_check:
        full_path = app_path / file_path
        if full_path.exists():
            print(f"   ✅ {description}: {file_path}")
        else:
            print(f"   ❌ {description}: {file_path} - НЕ НАЙДЕН!")
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
        from app.bot.filters.is_subscribed import IsSubscribed, NotSubscribed
        print("   ✅ Фильтры подписки импортированы")
    except ImportError as e:
        print(f"   ❌ Ошибка импорта фильтров: {e}")
        return False
    
    try:
        from app.bot.routers.misc.subscription_keyboard import subscription_required_keyboard, subscription_check_keyboard
        print("   ✅ Клавиатуры подписки импортированы")
    except ImportError as e:
        print(f"   ❌ Ошибка импорта клавиатур: {e}")
        return False
    
    try:
        from app.bot.routers.misc import subscription_handler
        print("   ✅ Обработчик подписки импортирован")
    except ImportError as e:
        print(f"   ❌ Ошибка импорта обработчика: {e}")
        return False
    
    print()
    print("✅ Все импорты работают корректно")
    print()
    
    # Проверяем интеграцию в роутеры
    print("🔗 Проверка интеграции в роутеры:")
    
    routers_to_check = [
        "app/bot/routers/main_menu/handler.py",
        "app/bot/routers/profile/handler.py", 
        "app/bot/routers/subscription/subscription_handler.py",
        "app/bot/routers/download/handler.py",
        "app/bot/routers/support/handler.py",
        "app/bot/routers/referral/handler.py",
    ]
    
    integration_ok = True
    for router_file in routers_to_check:
        full_path = app_path / router_file
        if full_path.exists():
            content = full_path.read_text(encoding='utf-8')
            if "IsSubscribed" in content:
                print(f"   ✅ {router_file.split('/')[-2]}: фильтр интегрирован")
            else:
                print(f"   ❌ {router_file.split('/')[-2]}: фильтр НЕ интегрирован")
                integration_ok = False
        else:
            print(f"   ❌ {router_file}: файл не найден")
            integration_ok = False
    
    print()
    
    if not integration_ok:
        print("❌ Фильтры подписки не полностью интегрированы в роутеры!")
        return False
    
    print("✅ Фильтры интегрированы во все роутеры")
    print()
    
    # Итоговый результат
    print("=" * 60)
    print("🎉 ТЕСТ ПРОЙДЕН УСПЕШНО!")
    print()
    print("📖 Инструкции по настройке:")
    print("   1. Получите реальный ID канала @DucksNet")
    print("   2. Замените -1001234567890 в config.py на реальный ID")
    print("   3. Запустите бота")
    print("   4. Пользователи без подписки будут блокированы")
    print()
    print("🔧 Для отключения системы установите:")
    print("   SHOP_FORCE_SUBSCRIPTION_ENABLED=false")
    print()
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_subscription_system())
    sys.exit(0 if success else 1)
