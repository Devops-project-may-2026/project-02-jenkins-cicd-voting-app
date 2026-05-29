## Local Docker Build

- Forked the repository to my GitHub account
- Cloned the fork locally
- Built and ran the app using docker-compose up --build
- Verified vote app at http://localhost:8080
- Verified result app at http://localhost:8081

## Jenkins CI/CD Pipeline

- Installed Jenkins locally via Docker
- Created DockerHub access token
- Added DockerHub credentials to Jenkins
- Written Jenkinsfile with 4 stages: Checkout, Build Images, Push Images, Deploy
- Successfully built Docker images for vote, result, worker
- Successfully pushed images to DockerHub (marta77784/vote, marta77784/result, marta77784/worker)
- Successfully deployed the app via docker-compose
- Pipeline status: SUCCESS