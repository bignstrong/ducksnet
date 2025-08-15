#!/bin/bash

# Скрипт для проверки здоровья сервисов ducksnet
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
    echo "Использование: $0 <environment>"
    echo "Environments:"
    echo "  production  - Продакшн сервер"
    echo "  staging     - Тестовый сервер"
    exit 1
fi

ENVIRONMENT=$1

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

log "🔍 Проверка здоровья сервисов в окружении: $ENVIRONMENT"

# Проверка Docker
if ! command -v docker &> /dev/null; then
    error "❌ Docker не установлен"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    error "❌ Docker Compose не установлен"
    exit 1
fi

info "✅ Docker и Docker Compose установлены"

# Проверка статуса контейнеров
log "🐳 Проверка статуса контейнеров..."
if docker-compose ps | grep -q "Up"; then
    info "✅ Контейнеры запущены"
    docker-compose ps
else
    error "❌ Контейнеры не запущены"
    docker-compose ps
    exit 1
fi

# Проверка здоровья бота
log "🤖 Проверка здоровья бота..."
if docker-compose exec -T bot curl -f http://localhost:8080/health 2>/dev/null; then
    info "✅ Бот работает корректно"
else
    warning "⚠️ Бот может быть не готов (health check недоступен)"
fi

# Проверка Redis
log "🔴 Проверка Redis..."
if docker-compose exec -T redis redis-cli --raw incr ping 2>/dev/null > /dev/null; then
    info "✅ Redis работает корректно"
    
    # Проверка памяти Redis
    MEMORY_INFO=$(docker-compose exec -T redis redis-cli info memory 2>/dev/null | grep "used_memory_human\|maxmemory_human" || echo "")
    if [ -n "$MEMORY_INFO" ]; then
        info "📊 Информация о памяти Redis:"
        echo "$MEMORY_INFO" | sed 's/^/  /'
    fi
else
    error "❌ Redis недоступен"
fi

# Проверка Traefik
log "🌐 Проверка Traefik..."
if docker-compose exec -T traefik traefik version 2>/dev/null; then
    info "✅ Traefik работает корректно"
    
    # Проверка конфигурации
    CONFIG_CHECK=$(docker-compose exec -T traefik traefik version 2>/dev/null | head -1 || echo "")
    info "📋 Версия Traefik: $CONFIG_CHECK"
else
    error "❌ Traefik недоступен"
fi

# Проверка базы данных
log "🗄️ Проверка базы данных..."
if docker-compose exec -T bot test -f /app/db/database.db 2>/dev/null; then
    info "✅ База данных существует"
    
    # Проверка миграций
    if docker-compose exec -T bot alembic current 2>/dev/null; then
        info "✅ Миграции применены"
    else
        warning "⚠️ Проблемы с миграциями"
    fi
else
    warning "⚠️ База данных не найдена"
fi

# Проверка сетевых соединений
log "🌐 Проверка сетевых соединений..."
NETWORK_INFO=$(docker network inspect ducksnet-network 2>/dev/null | grep -E '"Name"|"IPv4Address"' || echo "")
if [ -n "$NETWORK_INFO" ]; then
    info "✅ Docker сеть настроена"
else
    warning "⚠️ Проблемы с Docker сетью"
fi

# Проверка портов
log "🔌 Проверка открытых портов..."
PORTS_STATUS=""
if netstat -tulpn 2>/dev/null | grep -q ":80 "; then
    PORTS_STATUS="$PORTS_STATUS 80(HTTP)✅"
else
    PORTS_STATUS="$PORTS_STATUS 80(HTTP)❌"
fi

if netstat -tulpn 2>/dev/null | grep -q ":443 "; then
    PORTS_STATUS="$PORTS_STATUS 443(HTTPS)✅"
else
    PORTS_STATUS="$PORTS_STATUS 443(HTTPS)❌"
fi

if netstat -tulpn 2>/dev/null | grep -q ":22 "; then
    PORTS_STATUS="$PORTS_STATUS 22(SSH)✅"
else
    PORTS_STATUS="$PORTS_STATUS 22(SSH)❌"
fi

info "📡 Статус портов:$PORTS_STATUS"

# Проверка SSL сертификатов
log "🔒 Проверка SSL сертификатов..."
if [ -d "/opt/ducksnet/letsencrypt_data" ] || [ -d "/opt/ducksnet-staging/letsencrypt_data" ]; then
    info "✅ Директория Let's Encrypt существует"
    
    # Проверка срока действия сертификатов
    CERT_FILES=$(find /opt/ducksnet* -name "*.crt" -o -name "*.pem" 2>/dev/null | head -5)
    if [ -n "$CERT_FILES" ]; then
        info "📜 Найдены сертификаты:"
        echo "$CERT_FILES" | sed 's/^/  /'
    fi
else
    warning "⚠️ Директория Let's Encrypt не найдена"
fi

# Проверка логов на ошибки
log "📝 Проверка логов на ошибки..."
ERROR_COUNT=0

# Проверка логов бота
BOT_ERRORS=$(docker-compose logs --tail=100 bot 2>/dev/null | grep -i "error\|exception\|traceback" | wc -l)
if [ "$BOT_ERRORS" -gt 0 ]; then
    warning "⚠️ В логах бота найдено $BOT_ERRORS ошибок"
    ERROR_COUNT=$((ERROR_COUNT + BOT_ERRORS))
fi

# Проверка логов Traefik
TRAEFIK_ERRORS=$(docker-compose logs --tail=100 traefik 2>/dev/null | grep -i "error\|exception" | wc -l)
if [ "$TRAEFIK_ERRORS" -gt 0 ]; then
    warning "⚠️ В логах Traefik найдено $TRAEFIK_ERRORS ошибок"
    ERROR_COUNT=$((ERROR_COUNT + TRAEFIK_ERRORS))
fi

# Проверка логов Redis
REDIS_ERRORS=$(docker-compose logs --tail=100 redis 2>/dev/null | grep -i "error\|exception" | wc -l)
if [ "$REDIS_ERRORS" -gt 0 ]; then
    warning "⚠️ В логах Redis найдено $REDIS_ERRORS ошибок"
    ERROR_COUNT=$((ERROR_COUNT + REDIS_ERRORS))
fi

# Проверка использования ресурсов
log "💾 Проверка использования ресурсов..."
RESOURCE_INFO=$(docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" 2>/dev/null || echo "")
if [ -n "$RESOURCE_INFO" ]; then
    info "📊 Использование ресурсов:"
    echo "$RESOURCE_INFO"
else
    warning "⚠️ Не удалось получить информацию о ресурсах"
fi

# Проверка дискового пространства
log "💿 Проверка дискового пространства..."
DISK_INFO=$(df -h /opt 2>/dev/null | tail -1 || echo "")
if [ -n "$DISK_INFO" ]; then
    USAGE=$(echo "$DISK_INFO" | awk '{print $5}' | sed 's/%//')
    if [ "$USAGE" -gt 80 ]; then
        warning "⚠️ Диск заполнен на $USAGE%"
    else
        info "✅ Диск заполнен на $USAGE%"
    fi
    info "📊 Информация о диске:"
    echo "$DISK_INFO" | sed 's/^/  /'
fi

# Итоговая оценка
log "📋 Итоговая оценка здоровья системы:"

if [ "$ERROR_COUNT" -eq 0 ]; then
    info "🎉 Система работает отлично! Все проверки пройдены успешно."
    EXIT_CODE=0
elif [ "$ERROR_COUNT" -lt 5 ]; then
    warning "⚠️ Система работает с небольшими проблемами. Найдено $ERROR_COUNT ошибок."
    EXIT_CODE=1
else
    error "❌ Система имеет серьезные проблемы. Найдено $ERROR_COUNT ошибок."
    EXIT_CODE=2
fi

# Рекомендации
log "💡 Рекомендации:"
if [ "$ERROR_COUNT" -gt 0 ]; then
    echo "  - Проверьте логи сервисов: docker-compose logs -f [service_name]"
    echo "  - Перезапустите проблемные сервисы: docker-compose restart [service_name]"
    echo "  - Проверьте конфигурацию в .env файле"
fi

if [ "$USAGE" -gt 80 ]; then
    echo "  - Очистите неиспользуемые Docker образы: docker system prune -a"
    echo "  - Проверьте логи на размер: docker-compose logs --tail=1000 | wc -c"
fi

echo "  - Регулярно проверяйте здоровье системы: $0 $ENVIRONMENT"
echo "  - Настройте мониторинг и алерты"

log "🏁 Проверка здоровья завершена с кодом: $EXIT_CODE"
exit $EXIT_CODE
