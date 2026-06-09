pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
        DOCKERHUB_USERNAME = 'marta77784'
        IMAGE_TAG = "${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo 'Code checked out successfully'
            }
        }

        stage('Build Docker Images') {
            steps {
                sh 'docker build -t ${DOCKERHUB_USERNAME}/vote:${IMAGE_TAG} ./vote'
                sh 'docker build -t ${DOCKERHUB_USERNAME}/result:${IMAGE_TAG} ./result'
                sh 'docker build -t ${DOCKERHUB_USERNAME}/worker:${IMAGE_TAG} ./worker'
            }
        }

        stage('Push to DockerHub') {
            steps {
                sh 'echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin'
                sh 'docker push ${DOCKERHUB_USERNAME}/vote:${IMAGE_TAG}'
                sh 'docker push ${DOCKERHUB_USERNAME}/result:${IMAGE_TAG}'
                sh 'docker push ${DOCKERHUB_USERNAME}/worker:${IMAGE_TAG}'
            }
        }

        stage('Archive Build Info') {
            steps {
                sh 'echo "Build: ${IMAGE_TAG}" > build-info.txt'
                sh 'echo "vote:${IMAGE_TAG}" >> build-info.txt'
                sh 'echo "result:${IMAGE_TAG}" >> build-info.txt'
                sh 'echo "worker:${IMAGE_TAG}" >> build-info.txt'
                archiveArtifacts artifacts: 'build-info.txt'
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
