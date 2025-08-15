# 🚀 Автоматический деплой DucksNet

Этот документ описывает, как настроить автоматический деплой вашего Telegram бота DucksNet на сервер через GitHub Actions.

## 📋 Требования

- VPS сервер с Ubuntu 20.04+ или Debian 11+
- Домен с настроенными DNS записями
- GitHub репозиторий с кодом
- SSH ключ для доступа к серверу

## 🔧 Настройка сервера

### 1. Автоматическая настройка

Запустите скрипт настройки на сервере:

```bash
# Скачайте скрипт
curl -O https://raw.githubusercontent.com/your-username/DucksNet/main/scripts/setup_server.sh

# Сделайте исполняемым
chmod +x setup_server.sh

# Запустите с sudo
sudo ./setup_server.sh
```

### 2. Ручная настройка (если автоматическая не подходит)

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Создание директории
sudo mkdir -p /opt/ducksnet
sudo chown $USER:$USER /opt/ducksnet
```

## ⚙️ Настройка переменных окружения

Создайте файл `.env` в `/opt/ducksnet/`:

```bash
# Bot Configuration
BOT_TOKEN=your_bot_token_here
BOT_DOMAIN=your-domain.com

# Database
DATABASE_URL=sqlite:///app/db/database.db

# Redis
REDIS_PASSWORD=your_redis_password_here

# Let's Encrypt
LETSENCRYPT_EMAIL=your-email@example.com

# Traefik Dashboard Auth (username:password)
TRAEFIK_AUTH=admin:your_password_hash_here

# VPN Configuration
XUI_PANEL_URL=https://your-xui-panel.com
XUI_USERNAME=your_username
XUI_PASSWORD=your_password

# Payment Gateways
YOOKASSA_SHOP_ID=your_shop_id
YOOKASSA_SECRET_KEY=your_secret_key
CRYPTOMUS_MERCHANT_ID=your_merchant_id
CRYPTOMUS_PAYMENT_KEY=your_payment_key
```

### Генерация хеша пароля для Traefik:

```bash
echo -n 'admin:password' | base64
```

## 🔑 Настройка GitHub Secrets

В настройках вашего GitHub репозитория (`Settings` → `Secrets and variables` → `Actions`) добавьте:

### Обязательные секреты:

- `SERVER_HOST` - IP адрес или домен вашего сервера
- `SERVER_USER` - имя пользователя для SSH (обычно `ducksnet`)
- `SERVER_SSH_KEY` - приватный SSH ключ для доступа к серверу
- `SERVER_PORT` - SSH порт (обычно `22`)

### Дополнительные секреты:

- `TELEGRAM_BOT_TOKEN` - токен бота для уведомлений
- `TELEGRAM_CHAT_ID` - ID чата для уведомлений

## 🚀 Первый деплой

### 1. Склонируйте репозиторий на сервер:

```bash
cd /opt/ducksnet
git clone https://github.com/your-username/DucksNet.git .
```

### 2. Настройте .env файл

### 3. Запустите сервисы:

```bash
sudo systemctl start ducksnet
sudo systemctl enable ducksnet
```

### 4. Проверьте статус:

```bash
sudo systemctl status ducksnet
docker-compose ps
```

## 📱 GitHub Actions Workflow

После настройки секретов, при каждом push в ветку `main` будет автоматически:

1. ✅ Запускаться тесты
2. 🔍 Проверяться качество кода
3. 🐳 Собираться Docker образ
4. 🚀 Деплоиться на сервер
5. 📱 Отправляться уведомление в Telegram

### Ручной запуск деплоя:

1. Перейдите в `Actions` → `Deploy to Server`
2. Нажмите `Run workflow`
3. Выберите окружение (`production` или `staging`)
4. Нажмите `Run workflow`

## 🔍 Мониторинг

### Traefik Dashboard:

- URL: `https://traefik.your-domain.com`
- Логин: `admin`
- Пароль: указанный в `.env`

### Логи сервисов:

```bash
# Логи бота
docker-compose logs -f bot

# Логи Traefik
docker-compose logs -f traefik

# Логи Redis
docker-compose logs -f redis
```

### Статус сервисов:

```bash
docker-compose ps
sudo systemctl status ducksnet
```

## 🛠️ Обновление

### Автоматическое (через GitHub Actions):

- Просто сделайте push в ветку `main`

### Ручное обновление:

```bash
cd /opt/ducksnet
./update.sh
```

## 🚨 Устранение неполадок

### Проблемы с Docker:

```bash
# Перезапуск Docker
sudo systemctl restart docker

# Очистка системы
docker system prune -a -f
```

### Проблемы с Traefik:

```bash
# Проверка конфигурации
docker-compose exec traefik traefik version

# Проверка логов
docker-compose logs traefik
```

### Проблемы с базой данных:

```bash
# Запуск миграций
docker-compose exec bot alembic upgrade head

# Проверка статуса
docker-compose exec bot alembic current
```

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи: `docker-compose logs -f [service_name]`
2. Проверьте статус: `docker-compose ps`
3. Проверьте GitHub Actions логи
4. Создайте issue в репозитории

## 🔒 Безопасность

- ✅ Все порты закрыты кроме 22, 80, 443
- ✅ Traefik Dashboard защищен базовой аутентификацией
- ✅ Redis защищен паролем
- ✅ Контейнеры запускаются от непривилегированного пользователя
- ✅ SSL сертификаты автоматически обновляются через Let's Encrypt
