# 🦆 DucksNet - Telegram Bot для VPN подписок

Telegram бот для продажи VPN подписок с интеграцией 3X-UI панели и множественными платежными системами.

## ✨ Возможности

- 🤖 Telegram Bot на aiogram 3.x
- 💳 Поддержка множественных платежных систем (YooKassa, CryptoMus, YooMoney, Telegram Stars, Heleket)
- 🔐 Интеграция с 3X-UI панелью
- 📊 Реферальная система
- 🎫 Система промокодов
- 📱 Уведомления и уведомления
- 🌐 Веб-интерфейс для администрирования
- 🐳 Docker контейнеризация
- 🔒 Автоматические SSL сертификаты через Let's Encrypt
- 📈 Мониторинг и логирование

## 🚀 Быстрый старт

### 1. Клонирование репозитория

```bash
git clone https://github.com/your-username/DucksNet.git
cd DucksNet
```

### 2. Настройка переменных окружения

```bash
cp env.example .env
# Отредактируйте .env файл с вашими настройками
```

### 3. Запуск через Docker

```bash
# Сборка и запуск
docker-compose up -d --build

# Просмотр логов
docker-compose logs -f bot
```

### 4. Локальная разработка

```bash
# Установка зависимостей
pip install poetry
poetry install

# Запуск бота
poetry run python app/__main__.py
```

## 🐳 Автоматический деплой

### Настройка GitHub Actions

1. **Добавьте секреты в GitHub:**
   - `SERVER_HOST` - IP адрес вашего сервера
   - `SERVER_USER` - имя пользователя для SSH
   - `SERVER_SSH_KEY` - приватный SSH ключ
   - `SERVER_PORT` - SSH порт (обычно 22)

2. **Автоматический деплой:**
   - При каждом push в ветку `main` бот автоматически деплоится на сервер
   - Ручной запуск через GitHub Actions → Deploy to Server

### Настройка сервера

   ```bash
# Автоматическая настройка
curl -O https://raw.githubusercontent.com/your-username/DucksNet/main/scripts/setup_server.sh
chmod +x setup_server.sh
sudo ./setup_server.sh

# Или ручная настройка
sudo apt update && sudo apt upgrade -y
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Первый деплой

  ```bash
# На сервере
cd /opt/ducksnet
git clone https://github.com/your-username/DucksNet.git .
# Настройте .env файл
sudo systemctl start ducksnet
sudo systemctl enable ducksnet
```

## 📁 Структура проекта

```
DucksNet/
├── app/                    # Основной код приложения
│   ├── bot/               # Telegram бот
│   ├── routers/           # Обработчики команд
│   ├── services/          # Бизнес-логика
│   ├── models/            # Модели данных
│   └── utils/             # Утилиты
├── db/                    # База данных и миграции
├── scripts/               # Скрипты деплоя и управления
├── docker-compose.yml     # Docker Compose конфигурация
├── Dockerfile             # Docker образ
└── .github/workflows/     # GitHub Actions
```

## 🔧 Конфигурация

### Основные настройки в .env:

   ```bash
# Bot Configuration
BOT_TOKEN=your_telegram_bot_token
BOT_DOMAIN=your-domain.com

# Database
DATABASE_URL=sqlite:///app/db/database.db

# Redis
REDIS_PASSWORD=your_redis_password

# Let's Encrypt
LETSENCRYPT_EMAIL=your-email@example.com

# VPN Panel
XUI_PANEL_URL=https://your-xui-panel.com
XUI_USERNAME=your_username
XUI_PASSWORD=your_password

# Payment Gateways
YOOKASSA_SHOP_ID=your_shop_id
YOOKASSA_SECRET_KEY=your_secret_key
```

## 📱 Использование

### Команды бота:

- `/start` - Главное меню
- `/profile` - Профиль пользователя
- `/subscription` - Управление подпиской
- `/referral` - Реферальная система
- `/support` - Поддержка

### Админ команды:

- `/admin` - Панель администратора
- `/stats` - Статистика
- `/users` - Управление пользователями
- `/maintenance` - Режим обслуживания

## 🔍 Мониторинг

### Traefik Dashboard:
- URL: `https://traefik.your-domain.com`
- Логин: `admin`
- Пароль: указанный в `.env`

### Логи:
```bash
# Логи бота
docker-compose logs -f bot

# Логи Traefik
docker-compose logs -f traefik

# Статус сервисов
docker-compose ps
```

## 🛠️ Разработка

### Установка зависимостей:

```bash
poetry install
poetry add package_name  # Добавить пакет
poetry remove package_name  # Удалить пакет
```

### Запуск тестов:

```bash
poetry run pytest
poetry run flake8 app/
poetry run black app/
```

### Миграции базы данных:

```bash
poetry run alembic revision --autogenerate -m "Description"
poetry run alembic upgrade head
```

## 🚨 Устранение неполадок

### Проблемы с Docker:
```bash
docker system prune -a -f
sudo systemctl restart docker
```

### Проблемы с базой данных:
```bash
docker-compose exec bot alembic upgrade head
docker-compose exec bot alembic current
```

### Проблемы с SSL:
```bash
docker-compose logs traefik
docker-compose exec traefik traefik version
```

## 📚 Документация

- [📖 Подробная инструкция по деплою](DEPLOYMENT.md)
- [🐳 Docker руководство](Dockerfile)
- [⚙️ Конфигурация](env.example)

## 🤝 Поддержка

При возникновении проблем:

1. Проверьте логи: `docker-compose logs -f [service_name]`
2. Проверьте GitHub Actions логи
3. Создайте issue в репозитории
4. Проверьте документацию в `DEPLOYMENT.md`

## 📄 Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE) для деталей.

## 🙏 Благодарности

- [aiogram](https://github.com/aiogram/aiogram) - Асинхронный фреймворк для Telegram Bot API
- [3X-UI](https://github.com/alireza0/x-ui) - Панель управления Xray
- [Traefik](https://traefik.io/) - Reverse proxy и load balancer

---

**Удачного использования! 🎉**
