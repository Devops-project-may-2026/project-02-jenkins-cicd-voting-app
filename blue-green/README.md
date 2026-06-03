# Blue-Green Deployment Guide

## Overview
Blue-Green deployment allows zero-downtime releases with automatic rollback on failure.

## How it works
User Request -> Nginx (port 80) -> Blue (8080/8081) OR Green (8180/8181)

## Prerequisites
- AWS EC2 instance (Ubuntu 24.04, t2.medium)
- Docker and Docker Compose installed
- Nginx installed
- Open ports: 22, 80, 8080, 8081, 8180, 8181

## Setup

Install Docker and Docker Compose:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io docker-compose nginx
sudo usermod -aG docker ubuntu
```

Copy scripts to server:
```bash
scp -i your-key.pem -r blue-green ubuntu@YOUR_IP:~/
```

## Deployment

Start Blue:
```bash
docker-compose -f ~/blue-green/docker-compose.blue.yml up -d
bash ~/blue-green/smoke-test.sh blue
```

Deploy Green:
```bash
docker-compose -f ~/blue-green/docker-compose.green.yml up -d
bash ~/blue-green/smoke-test.sh green
sudo bash ~/blue-green/switch-traffic.sh blue green
```

Rollback to Blue:
```bash
docker-compose -f ~/blue-green/docker-compose.green.yml down
sudo bash ~/blue-green/switch-traffic.sh green blue
```

## Environment
- AWS EC2: Ubuntu 24.04, t2.medium
- Docker: 29.1.3
- Nginx: latest
- Deployment host: 18.207.125.109
