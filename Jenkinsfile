pipeline {
    agent any

    environment {
        DOCKER_HUB_CREDENTIALS = credentials('dockerhub')
        DOCKER_HUB_USERNAME = 'marta77784'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Images') {
            steps {
                sh 'docker build -t $DOCKER_HUB_USERNAME/vote:latest ./vote'
                sh 'docker build -t $DOCKER_HUB_USERNAME/result:latest ./result'
                sh 'docker build -t $DOCKER_HUB_USERNAME/worker:latest ./worker'
            }
        }

        stage('Push Images') {
            steps {
                sh 'echo $DOCKER_HUB_CREDENTIALS_PSW | docker login -u $DOCKER_HUB_USERNAME --password-stdin'
                sh 'docker push $DOCKER_HUB_USERNAME/vote:latest'
                sh 'docker push $DOCKER_HUB_USERNAME/result:latest'
                sh 'docker push $DOCKER_HUB_USERNAME/worker:latest'
                                                                                       sh 'docker-compose down --remove-orphans || true'
                sh 'docker-compose up -d'
            }
        }
    }
}
