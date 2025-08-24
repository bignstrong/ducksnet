#!/usr/bin/env python3
"""
Быстрая проверка статуса системы принудительной подписки.
"""
import os
from pathlib import Path

def main():
    print("🔍 Быстрая проверка системы принудительной подписки")
    print("=" * 60)
    
    project_path = Path(__file__).parent.parent
    
    # Основные файлы системы
    key_files = [
        "app/bot/filters/is_subscribed.py",
        "app/bot/routers/misc/subscription_handler.py", 
        "app/bot/routers/misc/subscription_keyboard.py",
        ".env.example",
        "SUBSCRIPTION_SETUP.md"
    ]
    
    print("📂 Основные файлы:")
    all_files_ok = True
    for file_path in key_files:
        full_path = project_path / file_path
        if full_path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - отсутствует!")
            all_files_ok = False
    
    print()
    
    # Проверка .env
    env_file = project_path / ".env"
    env_example = project_path / ".env.example"
    
    print("⚙️ Конфигурация:")
    if env_file.exists():
        print("   ✅ Файл .env существует")
        # Проверяем настройки подписки в .env
        env_content = env_file.read_text(encoding='utf-8')
        if "SHOP_FORCE_SUBSCRIPTION_ENABLED" in env_content:
            print("   ✅ Настройки подписки найдены в .env")
        else:
            print("   ⚠️  Настройки подписки не найдены в .env")
    else:
        print("   ⚠️  Файл .env не найден")
        if env_example.exists():
            print("   📝 Скопируйте .env.example в .env для настройки")
    
    print()
    
    # Итоговый статус
    if all_files_ok:
        print("🎉 СИСТЕМА ГОТОВА К НАСТРОЙКЕ!")
        print()
        print("📋 Следующие шаги:")
        if not env_file.exists():
            print("   1. Скопируйте .env.example в .env")
            print("      cp .env.example .env")
        print("   2. Получите ID канала через @userinfobot")
        print("   3. Настройте переменные в .env:")
        print("      SHOP_FORCE_SUBSCRIPTION_ENABLED=true")
        print("      SHOP_FORCE_SUBSCRIPTION_CHANNEL_ID=-100XXXXXXXXX")
        print("      SHOP_FORCE_SUBSCRIPTION_CHANNEL_USERNAME=DucksNet")
        print("   4. Добавьте бота в канал как админа")
        print("   5. Запустите бота!")
        print()
        print("📖 Подробная инструкция: SUBSCRIPTION_SETUP.md")
    else:
        print("❌ Не все файлы системы установлены!")
        print("   Переустановите систему принудительной подписки")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
