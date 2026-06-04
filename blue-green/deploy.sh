#!/bin/bash

echo "Starting Blue-Green deployment..."

# Detect which environment is currently active by reading nginx config.
# This ensures we always deploy to the INACTIVE environment.
if grep -q "8180" /etc/nginx/sites-available/voting-app 2>/dev/null; then
    CURRENT="green"
    TARGET="blue"
else
    # Default: assume blue is active (first deploy or no nginx config yet)
    CURRENT="blue"
    TARGET="green"
fi

echo "Current: $CURRENT | Target: $TARGET"

# Step 1 - Start the target environment
echo "Starting $TARGET environment..."
docker compose -f blue-green/docker-compose.${TARGET}.yml up -d

# Step 2 - Wait for containers to be ready
echo "Waiting for $TARGET to start..."
sleep 10

# Step 3 - Run smoke tests
echo "Running smoke tests..."
bash blue-green/smoke-test.sh $TARGET

if [ $? -eq 0 ]; then
    # Tests passed - switch nginx traffic to target
    echo "Smoke tests passed! Switching traffic to $TARGET..."
    sudo bash blue-green/switch-traffic.sh $CURRENT $TARGET

    # Tear down the old environment
    echo "Stopping $CURRENT environment..."
    docker compose -f blue-green/docker-compose.${CURRENT}.yml down

    echo "Deployment successful! Now running on $TARGET"
else
    # Tests failed - roll back by tearing down target, current stays live
    echo "Smoke tests failed! Rolling back to $CURRENT..."
    docker compose -f blue-green/docker-compose.${TARGET}.yml down
    echo "Rollback complete! Still running on $CURRENT"
    exit 1
fi
