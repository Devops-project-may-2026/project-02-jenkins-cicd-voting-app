# Jenkins Setup Guide

## Prerequisites

- Jenkins installed and running
- Docker Hub account

## Configure Jenkins Credentials

1. Go to **Manage Jenkins** → **Credentials** → **System** → **Global credentials**
2. Click **Add Credentials**
3. Fill in:
   - **Kind:** Username with password
   - **ID:** `dockerhub-credentials`
   - **Username:** your Docker Hub username
   - **Password:** your Docker Hub access token (not your login password)
   - Generate token at: hub.docker.com → Account Settings → Security → Personal access tokens

## Create Pipeline Job

1. Click **New Item**
2. Enter name: `voting-app-pipeline`
3. Select **Pipeline**
4. Under Pipeline section select **Pipeline script from SCM**
5. SCM: **Git**
6. Repository URL: your fork URL
7. Branch: your branch name
8. Script Path: `Jenkinsfile`
8. Click **Save**
9. Click **Build Now**
