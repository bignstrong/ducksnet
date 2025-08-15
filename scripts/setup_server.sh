#!/bin/bash

# Скрипт для настройки сервера ducksnet
set -e

echo "🚀 Настройка сервера ducksnet..."

# Проверка на root права
if [ "$EUID" -ne 0 ]; then
    echo "❌ Требуются root права. Запустите с sudo"
    exit 1
fi

# Обновление системы
echo "📦 Обновление системы..."
apt update && apt upgrade -y

# Установка необходимых пакетов
echo "🔧 Установка необходимых пакетов..."
apt install -y \
    curl \
    wget \
    git \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release

# Установка Docker
echo "🐳 Установка Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt update
    apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
fi

# Установка Docker Compose
echo "📋 Установка Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Создание пользователя для приложения
echo "👤 Создание пользователя ducksnet..."
if ! id "ducksnet" &>/dev/null; then
    useradd -m -s /bin/bash ducksnet
    usermod -aG docker ducksnet
fi

# Создание директории для приложения
echo "📁 Создание директории приложения..."
mkdir -p /opt/ducksnet
chown ducksnet:ducksnet /opt/ducksnet

# Создание .env файла
echo "⚙️ Создание .env файла..."
cat > /opt/ducksnet/.env << 'EOF'
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
EOF

chown ducksnet:ducksnet /opt/ducksnet/.env
chmod 600 /opt/ducpsnet/.env

# Создание systemd сервиса для автозапуска
echo "🔄 Создание systemd сервиса..."
cat > /etc/systemd/system/ducksnet.service << 'EOF'
[Unit]
Description=ducksnet Bot
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/ducksnet
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0
User=ducksnet
Group=ducksnet

[Install]
WantedBy=multi-user.target
EOF

# Включение автозапуска
systemctl daemon-reload
systemctl enable ducksnet.service

# Настройка firewall
echo "🔥 Настройка firewall..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Создание скрипта для обновления
echo "📝 Создание скрипта обновления..."
cat > /opt/ducksnet/update.sh << 'EOF'
#!/bin/bash
cd /opt/ducksnet
git pull origin main
docker-compose down
docker-compose up -d --build
docker system prune -f
EOF

chmod +x /opt/ducksnet/update.sh
chown ducksnet:ducksnet /opt/ducksnet/update.sh

echo "✅ Настройка сервера завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Отредактируйте /opt/ducksnet/.env файл с вашими настройками"
echo "2. Склонируйте ваш репозиторий в /opt/ducksnet"
echo "3. Запустите: sudo systemctl start ducksnet"
echo "4. Проверьте статус: sudo systemctl status ducksnet"
echo ""
echo "🔐 Для генерации хеша пароля Traefik используйте:"
echo "echo -n 'admin:password' | base64"
echo ""
echo "🌐 Traefik Dashboard будет доступен по адресу: https://traefik.your-domain.com"
