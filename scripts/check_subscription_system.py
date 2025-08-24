#!/usr/bin/env python3
"""
Простая проверка системы принудительной подписки без зависимостей.
"""
import os
import sys
from pathlib import Path

def check_file_exists(file_path, description):
    """Проверяет существование файла."""
    if file_path.exists():
        print(f"   ✅ {description}")
        return True
    else:
        print(f"   ❌ {description} - НЕ НАЙДЕН!")
        return False

def check_file_contains(file_path, search_text, description):
    """Проверяет содержимое файла."""
    try:
        if file_path.exists():
            content = file_path.read_text(encoding='utf-8')
            if search_text in content:
                print(f"   ✅ {description}")
                return True
            else:
                print(f"   ❌ {description} - НЕ НАЙДЕНО!")
                return False
        else:
            print(f"   ❌ {description} - ФАЙЛ НЕ НАЙДЕН!")
            return False
    except Exception as e:
        print(f"   ❌ {description} - ОШИБКА: {e}")
        return False

def main():
    """Основная функция проверки."""
    
    print("🧪 Проверка системы принудительной подписки на канал")
    print("=" * 60)
    
    # Получаем путь к проекту
    project_path = Path(__file__).parent.parent
    
    print(f"📁 Проект: {project_path}")
    print()
    
    # 1. Проверяем основные файлы системы
    print("1️⃣ Проверка основных файлов:")
    
    files_check = []
    
    # Фильтры
    files_check.append(check_file_exists(
        project_path / "app/bot/filters/is_subscribed.py",
        "Фильтры подписки (is_subscribed.py)"
    ))
    
    # Обработчик
    files_check.append(check_file_exists(
        project_path / "app/bot/routers/misc/subscription_handler.py",
        "Обработчик подписки (subscription_handler.py)"
    ))
    
    # Клавиатуры
    files_check.append(check_file_exists(
        project_path / "app/bot/routers/misc/subscription_keyboard.py",
        "Клавиатуры подписки (subscription_keyboard.py)"
    ))
    
    # Локализация
    files_check.append(check_file_exists(
        project_path / "app/locales/ru/LC_MESSAGES/bot.po",
        "Русская локализация"
    ))
    
    print()
    
    # 2. Проверяем содержимое ключевых файлов
    print("2️⃣ Проверка содержимого файлов:")
    
    content_check = []
    
    # Проверяем фильтры
    content_check.append(check_file_contains(
        project_path / "app/bot/filters/is_subscribed.py",
        "class IsSubscribed",
        "Класс IsSubscribed в фильтрах"
    ))
    
    content_check.append(check_file_contains(
        project_path / "app/bot/filters/is_subscribed.py",
        "class NotSubscribed",
        "Класс NotSubscribed в фильтрах"
    ))
    
    # Проверяем конфигурацию
    content_check.append(check_file_contains(
        project_path / "app/config.py",
        "FORCE_SUBSCRIPTION_ENABLED",
        "Настройки подписки в config.py"
    ))
    
    content_check.append(check_file_contains(
        project_path / "app/config.py",
        "DucksNet",
        "Канал DucksNet в конфигурации"
    ))
    
    # Проверяем локализацию
    content_check.append(check_file_contains(
        project_path / "app/locales/ru/LC_MESSAGES/bot.po",
        "subscription_required:message:not_subscribed",
        "Сообщения подписки в локализации"
    ))
    
    print()
    
    # 3. Проверяем интеграцию в роутеры
    print("3️⃣ Проверка интеграции в роутеры:")
    
    routers_check = []
    
    routers_to_check = [
        ("app/bot/routers/main_menu/handler.py", "Главное меню"),
        ("app/bot/routers/profile/handler.py", "Профиль"),
        ("app/bot/routers/subscription/subscription_handler.py", "Подписки"),
        ("app/bot/routers/download/handler.py", "Загрузки"),
        ("app/bot/routers/support/handler.py", "Поддержка"),
        ("app/bot/routers/referral/handler.py", "Реферальная система"),
    ]
    
    for router_file, description in routers_to_check:
        routers_check.append(check_file_contains(
            project_path / router_file,
            "IsSubscribed",
            f"{description} - фильтр IsSubscribed"
        ))
    
    print()
    
    # 4. Проверяем регистрацию роутера
    print("4️⃣ Проверка регистрации:")
    
    registration_check = []
    
    registration_check.append(check_file_contains(
        project_path / "app/bot/routers/__init__.py",
        "misc.subscription_handler.router",
        "Регистрация subscription_handler в роутерах"
    ))
    
    registration_check.append(check_file_contains(
        project_path / "app/bot/routers/misc/__init__.py",
        "subscription_handler",
        "Импорт subscription_handler в misc"
    ))
    
    registration_check.append(check_file_contains(
        project_path / "app/bot/filters/__init__.py",
        "IsSubscribed, NotSubscribed",
        "Экспорт фильтров подписки"
    ))
    
    print()
    
    # 5. Итоговый результат
    print("=" * 60)
    
    all_files = all(files_check)
    all_content = all(content_check)
    all_routers = all(routers_check)
    all_registration = all(registration_check)
    
    total_success = all_files and all_content and all_routers and all_registration
    
    if total_success:
        print("🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО!")
        print()
        print("✅ Система принудительной подписки установлена корректно!")
        print()
        print("=" * 70)
        print("📋 ИНСТРУКЦИЯ ПО АКТИВАЦИИ:")
        print()
        print("1️⃣ Скопируйте .env.example в .env:")
        print("   cp .env.example .env")
        print()
        print("2️⃣ Получите ID канала @DucksNet:")
        print("   • Добавьте @userinfobot в канал как админа")
        print("   • Отправьте сообщение в канал")
        print("   • Скопируйте ID (формат: -100XXXXXXXXX)")
        print()
        print("3️⃣ Отредактируйте .env файл:")
        print("   SHOP_FORCE_SUBSCRIPTION_ENABLED=true")
        print("   SHOP_FORCE_SUBSCRIPTION_CHANNEL_ID=-100XXXXXXXXX")
        print("   SHOP_FORCE_SUBSCRIPTION_CHANNEL_USERNAME=DucksNet")
        print()
        print("4️⃣ Добавьте бота в канал как администратора")
        print()
        print("5️⃣ Запустите бота и протестируйте!")
        print()
        print("📖 Подробная инструкция: SUBSCRIPTION_SETUP.md")
        print("=" * 70)
        
    else:
        print("❌ ОБНАРУЖЕНЫ ПРОБЛЕМЫ!")
        print()
        if not all_files:
            print("   - Отсутствуют некоторые файлы системы")
        if not all_content:
            print("   - Проблемы с содержимым файлов")
        if not all_routers:
            print("   - Фильтры не интегрированы в некоторые роутеры")
        if not all_registration:
            print("   - Проблемы с регистрацией компонентов")
    
    print()
    return total_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
