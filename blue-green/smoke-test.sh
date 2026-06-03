#!/bin/bash

ENV=$1  # blue или green

if [ "$ENV" = "green" ]; then
  VOTE_PORT=8180
  RESULT_PORT=8181
else
  VOTE_PORT=8080
  RESULT_PORT=8081
fi

HOST=localhost

echo "Running smoke tests for $ENV environment..."

# Тест 1 — проверяем vote
echo "Testing vote app on port $VOTE_PORT..."
VOTE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://$HOST:$VOTE_PORT)
if [ "$VOTE_STATUS" = "200" ]; then
  echo "✅ Vote app is UP (HTTP $VOTE_STATUS)"
else
  echo "❌ Vote app is DOWN (HTTP $VOTE_STATUS)"
  exit 1
fi

# Тест 2 — проверяем result
echo "Testing result app on port $RESULT_PORT..."
RESULT_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://$HOST:$RESULT_PORT)
if [ "$RESULT_STATUS" = "200" ]; then
  echo "✅ Result app is UP (HTTP $RESULT_STATUS)"
else
  echo "❌ Result app is DOWN (HTTP $RESULT_STATUS)"
  exit 1
fi

echo "✅ All smoke tests passed for $ENV!"
exit 0
