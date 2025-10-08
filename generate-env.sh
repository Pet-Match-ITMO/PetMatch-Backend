#!/bin/bash

# Скрипт для генерации .env файла из переменных окружения
# Используется в CI/CD для автоматического создания конфигурации

set -e

ENV_FILE=".env"

echo "🔧 Генерируем .env файл..."

# Проверяем обязательные переменные
required_vars=(
    "DB_URL"
    "POSTGRES_DB" 
    "POSTGRES_USER"
    "POSTGRES_PASSWORD"
    "JWT_SECRET"
    "QUART_SCHEMA_CONVERT_CASING"
    "ML_API_URL"
    "REDIS_HOST"
    "REDIS_PORT"
    "REDIS_DB"
    "REDIS_PASSWORD"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Ошибка: переменная $var не установлена"
        exit 1
    fi
done

# Создаем .env файл
# Преобразуем DB_URL для использования asyncpg в приложении
ASYNC_DB_URL=$(echo "$DB_URL" | sed 's/postgresql:/postgresql+asyncpg:/')

cat > "$ENV_FILE" << EOF
# Database Configuration
DB_URL=${ASYNC_DB_URL}
ALEMBIC_DB_URL=${DB_URL}
POSTGRES_DB=${POSTGRES_DB}
POSTGRES_USER=${POSTGRES_USER}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

# JWT Configuration
JWT_SECRET=${JWT_SECRET}

# Quart Configuration
QUART_SCHEMA_CONVERT_CASING=${QUART_SCHEMA_CONVERT_CASING}

# ML API Configuration
ML_API_URL=${ML_API_URL}

# Redis Configuration
REDIS_HOST=${REDIS_HOST}
REDIS_PORT=${REDIS_PORT}
REDIS_DB=${REDIS_DB}
REDIS_PASSWORD=${REDIS_PASSWORD}

# Generated at: $(date)
EOF

# Устанавливаем безопасные права
chmod 600 "$ENV_FILE"

echo "✅ .env файл создан: $ENV_FILE"
echo "🔒 Права установлены: 600 (только владелец может читать/писать)"

# Показываем содержимое (без секретов)
echo ""
echo "📋 Содержимое .env файла:"
echo "========================"
sed 's/=.*/=***/' "$ENV_FILE"
echo "========================"
