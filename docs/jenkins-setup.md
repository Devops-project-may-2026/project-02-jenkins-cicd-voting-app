# Jenkins Setup Guide

This document explains how to provision Jenkins for the project and reproduce the Epic 2 setup.

## 1. AWS EC2 Instance

Recommended instance:

- AMI: Ubuntu Server 24.04 LTS
- Instance type: t3.small or higher
- Storage: 20-30 GB
- Security Group inbound rules:
  - SSH: port 22
  - Jenkins UI: port 8080
  - Jenkins agent port: port 50000

Example Jenkins URL:

```text
http://<EC2_PUBLIC_IP>:8080
```

Do not commit real public IPs, passwords, private keys, or tokens to the repository.

## 2. Install Java 21

```bash
sudo apt update
sudo apt install -y openjdk-21-jre
java -version
```

## 3. Install Jenkins

```bash
sudo wget -O /etc/apt/keyrings/jenkins-keyring.asc https://pkg.jenkins.io/debian-stable/jenkins.io-2026.key
echo "deb [signed-by=/etc/apt/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/" | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null

sudo apt update
sudo apt install -y jenkins
sudo systemctl enable jenkins
sudo systemctl start jenkins
sudo systemctl status jenkins --no-pager
```

## 4. Unlock Jenkins

Get the initial admin password:

```bash
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

Open Jenkins in the browser:

```text
http://<EC2_PUBLIC_IP>:8080
```

Install suggested plugins.

Required plugins:

- Git
- Pipeline
- GitHub plugin

## 5. Install Docker and Docker Compose

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-v2

docker --version
docker compose version
```

Allow Jenkins to run Docker commands:

```bash
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

## 6. Jenkins Job Configuration

Create a Jenkins Pipeline job.

Job name:

```text
project-02-jenkins-cicd-voting-app
```

Pipeline configuration:

- Definition: Pipeline script from SCM
- SCM: Git
- Repository URL: your fork URL
- Branch: main or feature branch being tested
- Script Path: Jenkinsfile

Enable build trigger:

```text
GitHub hook trigger for GITScm polling
```

## 7. GitHub Webhook

In GitHub repository settings:

```text
Settings -> Webhooks -> Add webhook
```

Payload URL:

```text
http://<EC2_PUBLIC_IP>:8080/github-webhook/
```

Content type:

```text
application/json
```

Event:

```text
Just the push event
```

## 8. Docker Hub Credentials Convention

For future Epic 3 Docker image push, use the following Jenkins credential ID:

```text
dockerhub-credentials
```

Credential type:

```text
Username with password
```

No Docker Hub username, password, or token should be stored in the repository.

## 9. Validation

Epic 2 validation:

- Jenkins server is running
- Jenkins job is connected to GitHub
- Jenkinsfile is pulled from the repository
- Pipeline completes successfully
- Build artifacts are archived
- GitHub webhook triggers Jenkins automatically after push
