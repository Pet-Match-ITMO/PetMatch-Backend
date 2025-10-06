#!/bin/bash

# Скрипт для создания пользователя deploy на сервере
# Запускать с правами sudo

set -e

DEPLOY_USER="deploy"
PROJECT_PATH="/opt/petmatch-backend"
KEY_NAME="deploy_key"
KEY_PATH="$HOME/.ssh/$KEY_NAME"

echo "🔧 Настройка автоматического деплоя..."
echo ""

# Функция для генерации SSH ключей
generate_ssh_keys() {
    echo "🔑 Проверяем SSH ключи для деплоя..."
    
    # Создаем директорию .ssh если её нет
    mkdir -p "$HOME/.ssh"
    chmod 700 "$HOME/.ssh"
    
    # Проверяем, существует ли уже ключ
    if [ -f "$KEY_PATH" ]; then
        echo "✅ SSH ключ для деплоя уже существует: $KEY_PATH"
        return 0
    fi
    
    echo "🔐 Создаем новый SSH ключ для деплоя..."
    ssh-keygen -t rsa -b 4096 -C "deploy@petmatch" -f "$KEY_PATH" -N ""
    
    echo "✅ SSH ключи созданы:"
    echo "   Приватный: $KEY_PATH"
    echo "   Публичный: $KEY_PATH.pub"
    echo ""
}

# Генерируем SSH ключи
generate_ssh_keys

echo "🔧 Создаем пользователя для деплоя..."

# Создаем пользователя deploy
if ! id "$DEPLOY_USER" &>/dev/null; then
    sudo useradd -m -s /bin/bash "$DEPLOY_USER"
    echo "✅ Пользователь $DEPLOY_USER создан"
else
    echo "ℹ️ Пользователь $DEPLOY_USER уже существует"
fi

# Добавляем в группу docker
sudo usermod -aG docker "$DEPLOY_USER"
echo "✅ Пользователь добавлен в группу docker"

# Создаем SSH директорию
sudo mkdir -p "/home/$DEPLOY_USER/.ssh"
sudo chown "$DEPLOY_USER:$DEPLOY_USER" "/home/$DEPLOY_USER/.ssh"
sudo chmod 700 "/home/$DEPLOY_USER/.ssh"

# Добавляем публичный ключ в authorized_keys
if [ -f "$KEY_PATH.pub" ]; then
    echo "🔑 Добавляем публичный ключ в authorized_keys..."
    sudo cp "$KEY_PATH.pub" "/home/$DEPLOY_USER/.ssh/authorized_keys"
    sudo chown "$DEPLOY_USER:$DEPLOY_USER" "/home/$DEPLOY_USER/.ssh/authorized_keys"
    sudo chmod 600 "/home/$DEPLOY_USER/.ssh/authorized_keys"
    echo "✅ Публичный ключ добавлен"
else
    echo "❌ Публичный ключ не найден: $KEY_PATH.pub"
    exit 1
fi

# Создаем директорию проекта
sudo mkdir -p "$PROJECT_PATH"
sudo chown "$DEPLOY_USER:$DEPLOY_USER" "$PROJECT_PATH"
echo "✅ Директория проекта создана: $PROJECT_PATH"

# Настраиваем sudo права для docker команд (опционально)
echo "$DEPLOY_USER ALL=(ALL) NOPASSWD: /usr/bin/docker, /usr/bin/docker-compose" | sudo tee "/etc/sudoers.d/$DEPLOY_USER"
echo "✅ Sudo права настроены"

echo ""
echo "🎉 Настройка деплоя завершена!"
echo ""
echo "📋 Настройки для GitHub Secrets:"
echo "SERVER_USER=$DEPLOY_USER"
echo "SERVER_PROJECT_PATH=$PROJECT_PATH"
echo ""
echo "🔐 Приватный ключ для GitHub Secret SERVER_SSH_KEY:"
echo "------------------------------------------------------------"
cat "$KEY_PATH"
echo "------------------------------------------------------------"
echo ""
echo "📝 Следующие шаги:"
echo "1. Скопируйте приватный ключ выше в GitHub Secret SERVER_SSH_KEY"
echo "2. Клонируйте репозиторий: sudo -u $DEPLOY_USER git clone <repo> $PROJECT_PATH"
echo "3. Создайте .env файл в проекте"
echo "4. Проверьте подключение: ssh -i $KEY_PATH $DEPLOY_USER@localhost"
echo ""
echo "✅ Готово! Теперь GitHub Actions может автоматически деплоить проект."
