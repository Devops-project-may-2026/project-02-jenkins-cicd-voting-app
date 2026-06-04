#!/bin/bash

echo "Starting Blue-Green deployment..."

# Определяем текущую и целевую среду
CURRENT="blue"
TARGET="green"

echo "Current: $CURRENT | Target: $TARGET"

# Шаг 1 — Запускаем Green
echo "Starting $TARGET environment..."
docker compose -f blue-green/docker-compose.green.yml up -d

# Шаг 2 — Ждём 10 секунд пока поднимется
echo "Waiting for $TARGET to start..."
sleep 10

# Шаг 3 — Запускаем smoke tests
echo "Running smoke tests..."
bash blue-green/smoke-test.sh $TARGET

if [ $? -eq 0 ]; then
  # Тесты прошли — переключаем трафик
  echo "Smoke tests passed! Switching traffic to $TARGET..."
  bash blue-green/switch-traffic.sh $CURRENT $TARGET
  
  # Останавливаем Blue
  echo "Stopping $CURRENT environment..."
  docker compose -f blue-green/docker-compose.blue.yml down
  
  echo "✅ Deployment successful! Running on $TARGET"
else
  # Тесты провалились — откат
  echo "❌ Smoke tests failed! Rolling back to $CURRENT..."
  docker compose -f blue-green/docker-compose.green.yml down
  echo "✅ Rollback complete! Still running on $CURRENT"
  exit 1
fi
