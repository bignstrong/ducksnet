#!/bin/bash

# Скрипт для быстрого деплоя ducksnet
set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Функции логирования
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Проверка аргументов
if [ $# -eq 0 ]; then
    echo "Использование: $0 <environment> [options]"
    echo "Environments:"
    echo "  production  - Продакшн сервер"
    echo "  staging     - Тестовый сервер"
    echo ""
    echo "Options:"
    echo "  --force     - Принудительная пересборка"
    echo "  --no-cache  - Без использования кэша Docker"
    echo "  --backup    - Создать бэкап перед деплоем"
    exit 1
fi

ENVIRONMENT=$1
shift

# Парсинг опций
FORCE_BUILD=false
NO_CACHE=false
CREATE_BACKUP=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --force)
            FORCE_BUILD=true
            shift
            ;;
        --no-cache)
            NO_CACHE=true
            shift
            ;;
        --backup)
            CREATE_BACKUP=true
            shift
            ;;
        *)
            error "Неизвестная опция: $1"
            exit 1
            ;;
    esac
done

# Проверка окружения
if [ "$ENVIRONMENT" != "production" ] && [ "$ENVIRONMENT" != "staging" ]; then
    error "Неверное окружение: $ENVIRONMENT"
    exit 1
fi

log "🚀 Начинаем деплой в окружение: $ENVIRONMENT"

# Определение директории проекта
PROJECT_DIR="/opt/ducksnet"
if [ "$ENVIRONMENT" = "staging" ]; then
    PROJECT_DIR="/opt/ducksnet-staging"
fi

# Проверка существования директории
if [ ! -d "$PROJECT_DIR" ]; then
    error "Директория проекта не найдена: $PROJECT_DIR"
    exit 1
fi

# Переход в директорию проекта
cd "$PROJECT_DIR"

# Проверка Docker
if ! command -v docker &> /dev/null; then
    error "Docker не установлен"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose не установлен"
    exit 1
fi

# Создание бэкапа
if [ "$CREATE_BACKUP" = true ]; then
    log "💾 Создание бэкапа..."
    BACKUP_DIR="$PROJECT_DIR/backups"
    mkdir -p "$BACKUP_DIR"
    
    BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).tar.gz"
    
    # Бэкап базы данных
    if docker-compose exec -T bot test -f /app/db/database.db 2>/dev/null; then
        docker-compose exec -T bot cp /app/db/database.db /tmp/database.db
        docker cp "$(docker-compose ps -q bot):/tmp/database.db" /tmp/database.db
        tar -czf "$BACKUP_FILE" -C /tmp database.db 2>/dev/null || true
        rm -f /tmp/database.db
    fi
    
    # Бэкап .env файла
    if [ -f .env ]; then
        tar -czf "$BACKUP_FILE" .env 2>/dev/null || true
    fi
    
    log "✅ Бэкап создан: $BACKUP_FILE"
fi

# Остановка сервисов
log "⏹️ Остановка сервисов..."
docker-compose down || true

# Очистка старых образов
log "🧹 Очистка старых образов..."
docker system prune -f

# Обновление кода
log "📥 Обновление кода..."
git fetch origin
git reset --hard origin/main

# Восстановление .env файла
if [ -f .env.backup ]; then
    log "⚙️ Восстановление .env файла..."
    cp .env.backup .env
fi

# Определение опций сборки
BUILD_OPTS=""
if [ "$FORCE_BUILD" = true ]; then
    BUILD_OPTS="$BUILD_OPTS --force-recreate"
fi

if [ "$NO_CACHE" = true ]; then
    BUILD_OPTS="$BUILD_OPTS --no-cache"
fi

# Запуск сервисов
log "🚀 Запуск сервисов..."
docker-compose up -d --build $BUILD_OPTS

# Ожидание готовности сервисов
log "⏳ Ожидание готовности сервисов..."
sleep 30

# Проверка статуса
log "🔍 Проверка статуса сервисов..."
docker-compose ps

# Проверка здоровья сервисов
log "🏥 Проверка здоровья сервисов..."
if docker-compose exec -T bot curl -f http://localhost:8080/health 2>/dev/null; then
    log "✅ Бот работает корректно"
else
    warning "⚠️ Бот может быть не готов"
fi

# Проверка Redis
if docker-compose exec -T redis redis-cli --raw incr ping 2>/dev/null > /dev/null; then
    log "✅ Redis работает корректно"
else
    warning "⚠️ Redis может быть не готов"
fi

# Проверка Traefik
if docker-compose exec -T traefik traefik version 2>/dev/null; then
    log "✅ Traefik работает корректно"
else
    warning "⚠️ Traefik может быть не готов"
fi

# Очистка
log "🧹 Финальная очистка..."
docker system prune -f

# Статистика
log "📊 Статистика деплоя:"
echo "  - Окружение: $ENVIRONMENT"
echo "  - Время деплоя: $(date)"
echo "  - Коммит: $(git rev-parse --short HEAD)"
echo "  - Ветка: $(git branch --show-current)"

log "🎉 Деплой завершен успешно!"
log "🌐 Проверьте доступность: https://$(grep BOT_DOMAIN .env | cut -d'=' -f2)"
log "📊 Traefik Dashboard: https://traefik.$(grep BOT_DOMAIN .env | cut -d'=' -f2)"

# Уведомление в Telegram (если настроено)
if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
    log "📱 Отправка уведомления в Telegram..."
    curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
        -d "chat_id=$TELEGRAM_CHAT_ID" \
        -d "text=🚀 ducksnet успешно развернут в $ENVIRONMENT!%0A✅ Статус: Работает%0A🌐 Домен: $(grep BOT_DOMAIN .env | cut -d'=' -f2)" \
        -d "parse_mode=HTML" > /dev/null 2>&1 || warning "Не удалось отправить уведомление"
fi
