#!/usr/bin/env python3
"""
Простой тест интеграции изображений для DucksNet бота.
"""
import sys
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Константы из конфигурации
DEFAULT_DATA_DIR = project_root / "app" / "data"
DEFAULT_MAIN_MENU_IMAGE_NAME = "DuckNetMainMenu.png"

def test_image_integration():
    """Тестирует интеграцию изображений."""
    print("🔍 Тестирование интеграции изображений DucksNet...")
    
    try:
        # Проверяем структуру файлов
        print("� Проверка структуры проекта...")
        
        # Проверяем папку с изображениями
        images_dir = DEFAULT_DATA_DIR / "images"
        print(f"�️  Папка изображений: {images_dir}")
        
        if images_dir.exists():
            print("✅ Папка изображений найдена!")
            print("📋 Содержимое папки:")
            for file in images_dir.iterdir():
                size_kb = file.stat().st_size / 1024 if file.is_file() else 0
                print(f"   - {file.name} ({size_kb:.1f} KB)")
        else:
            print("❌ Папка изображений НЕ найдена!")
            return
        
        # Проверяем конкретный файл изображения
        image_path = images_dir / DEFAULT_MAIN_MENU_IMAGE_NAME
        print(f"\n�️  Проверка главного изображения: {DEFAULT_MAIN_MENU_IMAGE_NAME}")
        
        if image_path.exists():
            print("✅ Файл главного изображения найден!")
            size_kb = image_path.stat().st_size / 1024
            print(f"📊 Размер файла: {size_kb:.1f} KB")
            
            # Проверяем размер файла
            if size_kb > 10240:  # 10 MB
                print("⚠️  Предупреждение: файл больше 10 МБ")
            elif size_kb < 50:  # 50 KB
                print("⚠️  Предупреждение: файл очень маленький")
            else:
                print("✅ Размер файла оптимальный!")
                
        else:
            print("❌ Файл главного изображения НЕ найден!")
            return
            
        # Проверяем утилиты
        print("\n�️  Проверка файлов утилит...")
        
        utils_path = project_root / "app" / "bot" / "utils" / "messaging.py"
        if utils_path.exists():
            print("✅ Файл messaging.py найден!")
        else:
            print("❌ Файл messaging.py НЕ найден!")
            
        # Проверяем middleware
        middleware_path = project_root / "app" / "bot" / "middlewares" / "config.py"
        if middleware_path.exists():
            print("✅ Файл config.py middleware найден!")
        else:
            print("❌ Файл config.py middleware НЕ найден!")
            
        # Проверяем роутеры
        print("\n� Проверка роутеров...")
        routers_to_check = [
            "main_menu/handler.py",
            "profile/handler.py", 
            "subscription/subscription_handler.py",
            "support/handler.py",
            "download/handler.py",
            "referral/handler.py"
        ]
        
        updated_routers = 0
        for router_path in routers_to_check:
            full_path = project_root / "app" / "bot" / "routers" / router_path
            if full_path.exists():
                # Проверяем наличие импорта messaging
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "from app.bot.utils.messaging import" in content:
                        print(f"   ✅ {router_path} - обновлен")
                        updated_routers += 1
                    else:
                        print(f"   ⚠️  {router_path} - не обновлен")
            else:
                print(f"   ❌ {router_path} - не найден")
                
        print(f"\n📊 Статистика обновления: {updated_routers}/{len(routers_to_check)} роутеров")
        
        # Финальный результат
        print("\n🎉 РЕЗУЛЬТАТ ТЕСТА:")
        if image_path.exists() and utils_path.exists() and middleware_path.exists():
            print("✅ Интеграция изображений полностью готова!")
            print("🚀 Все необходимые файлы на месте.")
            print("📝 Для активации добавьте в .env:")
            print("   SHOP_MAIN_MENU_IMAGE_ENABLED=true")
            print("   SHOP_MAIN_MENU_IMAGE_NAME=DuckNetMainMenu.png")
        else:
            print("❌ Интеграция НЕ завершена.")
            print("� Проверьте отсутствующие файлы выше.")
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        print(f"📋 Тип ошибки: {type(e).__name__}")


if __name__ == "__main__":
    test_image_integration()
