#!/bin/bash

CURRENT=$1  # blue или green
TARGET=$2   # blue или green

echo "Switching traffic from $CURRENT to $TARGET..."

# Устанавливаем порты
if [ "$TARGET" = "green" ]; then
  VOTE_PORT=8180
  RESULT_PORT=8181
else
  VOTE_PORT=8080
  RESULT_PORT=8081
fi

# Обновляем Nginx конфиг
sudo tee /etc/nginx/sites-available/voting-app << NGINX
server {
    listen 80;
    location /vote {
        proxy_pass http://localhost:${VOTE_PORT};
    }
    location / {
        proxy_pass http://localhost:${RESULT_PORT};
    }
}
NGINX

sudo nginx -t && sudo systemctl reload nginx
echo "Traffic switched to $TARGET!"
