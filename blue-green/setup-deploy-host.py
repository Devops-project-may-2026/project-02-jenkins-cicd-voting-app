#!/usr/bin/env python3
# setup-deploy-host.py
# One-time provisioning script for the blue-green deployment host EC2 instance.
# Run as: sudo python3 blue-green/setup-deploy-host.py
# Requirements: Ubuntu 22.04 / 24.04, Python 3.8+

import subprocess
import os
import sys
import textwrap

REPO_URL = "https://github.com/Devops-project-may-2026/project-02-jenkins-cicd-voting-app.git"
REPO_DIR = os.path.expanduser("~/project-02-jenkins-cicd-voting-app")
NGINX_SITE_NAME = "voting-app"
NGINX_SITES_AVAILABLE = "/etc/nginx/sites-available/voting-app"
NGINX_SITES_ENABLED = "/etc/nginx/sites-enabled/voting-app"
NGINX_DEFAULT_ENABLED = "/etc/nginx/sites-enabled/default"


def run(cmd, check=True, capture=False):
    print(f"  $ {cmd}")
    return subprocess.run(cmd, shell=True, check=check, capture_output=capture, text=True)


def step(title):
    print(f"\n{chr(61)*60}")
    print(f"  {title}")
    print(f"{chr(61)*60}")


def install_packages():
    step("1. Installing Docker, Docker Compose plugin, Nginx, Git")
    run("apt-get update -y")
    run("apt-get install -y ca-certificates curl gnupg lsb-release git nginx")
    run("install -m 0755 -d /etc/apt/keyrings")
    run("curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg")
    run("chmod a+r /etc/apt/keyrings/docker.gpg")
    run('echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list')
    run("apt-get update -y")
    run("apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin")
    print("  Docker and Compose v2 plugin installed.")


def add_user_to_docker(username):
    step(f"2. Adding user to docker group")
    run(f"usermod -aG docker {username}")
    print(f"  NOTE: {username} must log out and back in (or run newgrp docker) for this to take effect.")


def clone_repo():
    step("3. Cloning repository")
    if os.path.isdir(REPO_DIR):
        print(f"  Repo already exists at {REPO_DIR} - pulling latest.")
        run(f"git -C {REPO_DIR} pull --ff-only")
    else:
        run(f"git clone {REPO_URL} {REPO_DIR}")
    print(f"  Repo ready at {REPO_DIR}")


def create_env_file():
    step("4. Creating .env file for Docker Compose variable substitution")
    env_path = os.path.join(REPO_DIR, "blue-green", ".env")
    if os.path.exists(env_path):
        print(f"  .env already exists at {env_path} - skipping.")
        return
    docker_username = input("\n  Enter your DockerHub username (used as image prefix): ").strip()
    if not docker_username:
        print(f"  WARNING: No username entered. Manually create {env_path}")
        print("  File contents should be: DOCKER_USERNAME=yourusername")
        return
    with open(env_path, "w") as f:
        f.write(f"DOCKER_USERNAME={docker_username}\n")
    print(f"  Created {env_path} with DOCKER_USERNAME={docker_username}")


def configure_nginx():
    step("5. Configuring Nginx as blue/green traffic router")
    nginx_config = (
        "server {\n"
        "    listen 80;\n"
        "    server_name _;\n\n"
        "    # /vote/ -> blue port 8080, green port 8180 (switched by switch-traffic.sh)\n"
        "    location /vote/ {\n"
        "        proxy_pass http://localhost:8080/;\n"
        "        proxy_set_header Host $host;\n"
        "        proxy_set_header X-Real-IP $remote_addr;\n"
        "    }\n\n"
        "    # / -> result: blue port 8081, green port 8181\n"
        "    location / {\n"
        "        proxy_pass http://localhost:8081/;\n"
        "        proxy_set_header Host $host;\n"
        "        proxy_set_header X-Real-IP $remote_addr;\n"
        "    }\n"
        "}\n"
    )
    with open(NGINX_SITES_AVAILABLE, "w") as f:
        f.write(nginx_config)
    print(f"  Written nginx config to {NGINX_SITES_AVAILABLE}")
    if not os.path.exists(NGINX_SITES_ENABLED):
        os.symlink(NGINX_SITES_AVAILABLE, NGINX_SITES_ENABLED)
        print(f"  Symlinked to {NGINX_SITES_ENABLED}")
    else:
        print(f"  Symlink already exists at {NGINX_SITES_ENABLED}")
    if os.path.exists(NGINX_DEFAULT_ENABLED):
        os.remove(NGINX_DEFAULT_ENABLED)
        print("  Removed default nginx site to avoid port 80 conflict.")
    run("nginx -t")
    run("systemctl enable nginx")
    run("systemctl restart nginx")
    print("  Nginx configured and running.")


def configure_firewall():
    step("6. Configuring UFW firewall rules")
    result = run("which ufw", check=False, capture=True)
    if result.returncode != 0:
        print("  ufw not found - configure your AWS Security Group instead.")
        print("  Required inbound ports: 22 (SSH), 80 (HTTP), 8080, 8081 (blue), 8180, 8181 (green)")
        return
    for port in ["22/tcp", "80/tcp", "8080/tcp", "8081/tcp", "8180/tcp", "8181/tcp"]:
        run(f"ufw allow {port}")
    run("ufw --force enable")
    print("  Firewall rules applied.")


def print_jenkins_instructions():
    step("7. Jenkins configuration (manual steps required)")
    msg = """
    A) Add SSH credential for this deploy host:
       Manage Jenkins -> Credentials -> Global -> Add Credentials
         Kind:        SSH Username with private key
         ID:          deploy-host-ssh
         Username:    ubuntu
         Private key: (paste the contents of your EC2 .pem key file)

    B) Add deploy host IP as environment variable:
       Manage Jenkins -> System -> Global properties -> Environment variables
         Name:  DEPLOY_HOST
         Value: <this EC2 public IP or DNS name>

    C) In your pipeline job -> Build Triggers:
       [x] Poll SCM
       Schedule: H/5 * * * *
       This polls GitHub every 5 min - no webhook or static IP needed.

    D) Confirm dockerhub-credentials credential exists:
       Manage Jenkins -> Credentials -> Kind: Username with password
         ID:       dockerhub-credentials
         Username: your DockerHub username
         Password: your DockerHub access token

    Pipeline flow once configured:
      1. Jenkins polls GitHub every 5 min for commits to main
      2. Build images (vote, result, worker) tagged with GIT_SHA and latest
      3. Trivy security scan (reports archived) + security gate (fail on HIGH/CRITICAL)
      4. Push images to DockerHub
      5. SSH to DEPLOY_HOST, run blue-green/deploy.sh
      6. deploy.sh detects active env, starts the inactive one, runs smoke tests,
         switches nginx traffic on success, or tears down and keeps current on failure
    """
    print(msg)


def print_summary():
    step("Setup Complete")
    msg = f"""
    Deploy host is ready:
      Repo:   {REPO_DIR}
      .env:   {REPO_DIR}/blue-green/.env
      Nginx:  running on port 80, initially proxying to blue (8080/8081)
      Docker: installed with Compose v2 plugin (docker compose)

    Next: complete Jenkins steps above (step 7),
    then push a commit to main to trigger the first pipeline run.
    """
    print(msg)


def main():
    if os.geteuid() != 0:
        print("ERROR: This script must be run as root.")
        print("       sudo python3 blue-green/setup-deploy-host.py")
        sys.exit(1)
    sudo_user = os.environ.get("SUDO_USER", "ubuntu")
    install_packages()
    add_user_to_docker(sudo_user)
    clone_repo()
    create_env_file()
    configure_nginx()
    configure_firewall()
    print_jenkins_instructions()
    print_summary()


if __name__ == "__main__":
    main()
