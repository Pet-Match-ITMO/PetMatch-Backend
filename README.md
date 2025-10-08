# PetMatch-Backend

Backend for intelligent pet matching

## Переменные окружения

Для запуска приложения необходимо настроить следующие переменные окружения:

### Обязательные переменные

- `DB_URL` - URL подключения к PostgreSQL
- `POSTGRES_DB` - имя базы данных
- `POSTGRES_USER` - пользователь PostgreSQL
- `POSTGRES_PASSWORD` - пароль PostgreSQL
- `JWT_SECRET` - секретный ключ для JWT токенов
- `QUART_SCHEMA_CONVERT_CASING` - настройка конвертации регистра (обычно "true")

### Новые переменные для ML API и Redis

- `ML_API_URL` - URL ML API сервиса
- `REDIS_HOST` - хост Redis сервера
- `REDIS_PORT` - порт Redis сервера
- `REDIS_DB` - номер базы данных Redis

## Быстрый старт

1. Скопируйте `env.example` в `.env` и заполните переменные
2. Запустите `docker compose up -d`
