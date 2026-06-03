# Blue-Green Deployment Guide

## Overview
This guide describes the Blue-Green deployment strategy for the Voting App.
Blue-Green deployment allows zero-downtime releases with automatic rollback on failure.

## How it works
User Request
↓
Nginx (port 80)
↓
Blue (port 8080/8081) OR Green (port 8180/8181)

## Prerequisites
- AWS EC2 instance (Ubuntu 24.04, t2.medium)
- Docker and Docker Compose installed
- Nginx installed
- Open ports: 22, 80, 8080, 8081, 8180, 8181

## Setup

### 1. Install Docker and Docker Compose
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io docker-compose nginx
sudo usermod -aG docker ubuntu
```

### 2. Copy scripts to server
```bash
scp -i your-key.pem -r blue-green ubuntu@YOUR_IP:~/
```

## Deployment

### Start Blue environment
```bash
docker-compose -f ~/blue-green/docker-compose.blue.yml up -d
```

### Run smoke tests
```bash
bash ~/blue-green/smoke-test.sh blue
```

### Deploy Green environment
```bash
docker-compose -f ~/blue-green/docker-compose.green.yml up -d
bash ~/blue-green/smoke-test.sh green
```

### Switch traffic to Green
```bash
sudo bash ~/blue-green/switch-traffic.sh blue green
```

### Rollback to Blue
```bash
docker-compose -f ~/blue-green/docker-compose.green.yml down
sudo bash ~/blue-green/switch-traffic.sh green blue
```

## Smoke Tests
Smoke tests check that both services respond with HTTP 200:
- Vote app (port 8080 for Blue, 8180 for Green)
- Result app (port 8081 for Blue, 8181 for Green)

If smoke tests fail — rollback is triggered automatically.

## Environment
- AWS EC2: Ubuntu 24.04, t2.medium
- Docker: 29.1.3
- Docker Compose: 1.29.2
- Nginx: latest
- Deployment host IP: 18.207.125.109