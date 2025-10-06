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

# Функция для создания SSH ключа для GitHub
setup_github_ssh() {
    echo "🔑 Настраиваем SSH для GitHub..."
    
    GITHUB_KEY_PATH="/home/$DEPLOY_USER/.ssh/github_key"
    
    # Создаем SSH ключ для GitHub от имени deploy пользователя
    sudo -u "$DEPLOY_USER" ssh-keygen -t rsa -b 4096 -C "deploy@petmatch-github" -f "$GITHUB_KEY_PATH" -N ""
    
    # Создаем SSH config
    sudo -u "$DEPLOY_USER" tee "/home/$DEPLOY_USER/.ssh/config" > /dev/null << EOF
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/github_key
    IdentitiesOnly yes
EOF
    
    # Устанавливаем правильные права
    sudo chmod 600 "/home/$DEPLOY_USER/.ssh/config"
    sudo chmod 600 "$GITHUB_KEY_PATH"
    sudo chmod 644 "$GITHUB_KEY_PATH.pub"
    
    echo "✅ SSH ключ для GitHub создан"
}

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

# Настраиваем SSH для GitHub
setup_github_ssh

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
echo "🔑 SSH ключ для GitHub (добавьте в GitHub → Settings → SSH keys):"
echo "------------------------------------------------------------"
sudo cat "/home/$DEPLOY_USER/.ssh/github_key.pub"
echo "------------------------------------------------------------"
echo ""
echo "📝 Следующие шаги:"
echo "1. Скопируйте приватный ключ выше в GitHub Secret SERVER_SSH_KEY"
echo "2. Скопируйте SSH ключ для GitHub выше в GitHub → Settings → SSH and GPG keys"
echo "3. Клонируйте репозиторий:"
echo "   sudo -u $DEPLOY_USER git clone git@github.com:Pet-Match-ITMO/PetMatch-Backend.git $PROJECT_PATH"
echo "4. Создайте .env файл в проекте: sudo -u $DEPLOY_USER nano $PROJECT_PATH/.env"
echo "5. Проверьте SSH подключение: sudo -u $DEPLOY_USER ssh -T git@github.com"
echo ""
echo "✅ Готово! Теперь GitHub Actions может автоматически деплоить проект."
