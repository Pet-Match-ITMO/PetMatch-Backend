#!/bin/bash

# Скрипт для деплоя PetMatch Backend
# Используется GitHub Actions для автоматического деплоя

set -e

echo "🚀 Начинаем деплой PetMatch Backend..."

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден! Создайте его перед деплоем."
    exit 1
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
