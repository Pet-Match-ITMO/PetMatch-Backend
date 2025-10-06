#!/bin/bash

# Скрипт для деплоя PetMatch Backend
# Используется GitHub Actions для автоматического деплоя

set -e

echo "🚀 Начинаем деплой PetMatch Backend..."

# Генерируем .env файл если есть переменные окружения
if [ -n "$DB_URL" ] && [ -n "$JWT_SECRET" ]; then
    echo "🔧 Генерируем .env файл из переменных окружения..."
    ./generate-env.sh
elif [ ! -f .env ]; then
    echo "❌ Файл .env не найден и переменные окружения не установлены!"
    echo "Создайте .env файл или установите переменные окружения."
    exit 1
else
    echo "✅ Используем существующий .env файл"
fi

# Создаем общую сеть если её нет
echo "🌐 Проверяем общую сеть..."
if ! docker network ls | grep -q petmatch-network; then
    echo "🌐 Создаем общую сеть petmatch-network..."
    docker network create petmatch-network
    echo "✅ Сеть petmatch-network создана"
else
    echo "✅ Сеть petmatch-network уже существует"
fi

# Логинимся в GitHub Container Registry
echo "🔐 Авторизация в GitHub Container Registry..."
echo "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USERNAME" --password-stdin

# Останавливаем текущие контейнеры
echo "🛑 Останавливаем текущие контейнеры..."
docker compose -f docker-compose.prod.yaml down || true

# Загружаем новые образы
echo "📥 Загружаем новые образы..."
docker compose -f docker-compose.prod.yaml pull

# Запускаем миграции если нужно
echo "🗃️ Применяем миграции базы данных..."
docker compose -f docker-compose.prod.yaml run --rm app uv run alembic upgrade head

# Запускаем новые контейнеры
echo "🚀 Запускаем новые контейнеры..."
docker compose -f docker-compose.prod.yaml up -d

# Очищаем неиспользуемые образы
echo "🧹 Очищаем неиспользуемые образы..."
docker system prune -f

echo "✅ Деплой завершен успешно!"

# Показываем статус контейнеров
echo "📊 Статус контейнеров:"
docker compose -f docker-compose.prod.yaml ps
