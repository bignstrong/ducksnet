#!/usr/bin/env python3
"""
Утилита для обновления ID канала в конфигурации принудительной подписки.
"""
import re
import sys
from pathlib import Path

def update_channel_id(new_channel_id, new_username=None):
    """Обновляет ID канала в .env.example"""
    
    project_path = Path(__file__).parent.parent
    env_example_path = project_path / ".env.example"
    
    if not env_example_path.exists():
        print("❌ Файл .env.example не найден!")
        return False
    
    # Читаем содержимое
    content = env_example_path.read_text(encoding='utf-8')
    
    # Обновляем ID канала
    old_id_pattern = r'SHOP_FORCE_SUBSCRIPTION_CHANNEL_ID=-?\d+'
    new_id_line = f'SHOP_FORCE_SUBSCRIPTION_CHANNEL_ID={new_channel_id}'
    
    if re.search(old_id_pattern, content):
        content = re.sub(old_id_pattern, new_id_line, content)
        print(f"✅ ID канала обновлен на: {new_channel_id}")
    else:
        print("❌ Строка SHOP_FORCE_SUBSCRIPTION_CHANNEL_ID не найдена!")
        return False
    
    # Обновляем username если предоставлен
    if new_username:
        old_username_pattern = r'SHOP_FORCE_SUBSCRIPTION_CHANNEL_USERNAME=\w+'
        new_username_line = f'SHOP_FORCE_SUBSCRIPTION_CHANNEL_USERNAME={new_username}'
        
        if re.search(old_username_pattern, content):
            content = re.sub(old_username_pattern, new_username_line, content)
            print(f"✅ Username канала обновлен на: {new_username}")
    
    # Записываем обратно
    env_example_path.write_text(content, encoding='utf-8')
    
    return True

def main():
    print("🔧 Утилита обновления конфигурации канала")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("📋 Использование:")
        print("  python scripts/update_channel_config.py -100XXXXXXXXX [username]")
        print()
        print("📖 Примеры:")
        print("  python scripts/update_channel_config.py -1001234567890")
        print("  python scripts/update_channel_config.py -1001234567890 DucksNet")
        print()
        print("💡 Как получить ID канала:")
        print("  1. Добавьте @userinfobot в канал как админа")
        print("  2. Отправьте сообщение в канал")
        print("  3. Скопируйте ID из ответа бота")
        print()
        return
    
    new_channel_id = sys.argv[1]
    new_username = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Валидация ID канала
    if not new_channel_id.startswith('-100'):
        print("❌ ID канала должен начинаться с -100")
        print("   Пример правильного ID: -1001234567890")
        return
    
    if not new_channel_id[4:].isdigit():
        print("❌ ID канала должен содержать только цифры после -100")
        print("   Пример правильного ID: -1001234567890")
        return
    
    print(f"🔄 Обновление конфигурации...")
    print(f"   Новый ID канала: {new_channel_id}")
    if new_username:
        print(f"   Новый username: {new_username}")
    print()
    
    success = update_channel_id(new_channel_id, new_username)
    
    if success:
        print("🎉 Конфигурация успешно обновлена!")
        print()
        print("📋 Следующие шаги:")
        print("  1. Скопируйте .env.example в .env на сервере")
        print("  2. Убедитесь, что бот добавлен в канал как админ")
        print("  3. Перезапустите бота: docker compose restart ducksnet-bot")
        print("  4. Проверьте логи: docker compose logs ducksnet-bot")
    else:
        print("❌ Ошибка при обновлении конфигурации!")

if __name__ == "__main__":
    main()
