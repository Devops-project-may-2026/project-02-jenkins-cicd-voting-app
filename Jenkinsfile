pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code from GitHub...'
                checkout scm
            }
        }

        stage('Validate Docker Compose') {
            steps {
                echo 'Validating docker-compose.yml file...'
                sh 'docker compose config'
            }
        }

        stage('Build') {
            steps {
                echo 'Building application services with Docker Compose...'
                sh 'docker compose build'
            }
        }

        stage('Basic Tests') {
            steps {
                echo 'Running basic project checks...'
                sh 'test -f docker-compose.yml'
                sh 'test -d vote'
                sh 'test -d result'
                sh 'test -d worker'
            }
        }

        stage('Create Build Artifact') {
            steps {
                echo 'Creating basic build artifact...'
                sh '''
                    mkdir -p artifacts
                    echo "Build Number: ${BUILD_NUMBER}" > artifacts/build-info.txt
                    echo "Git Branch: ${BRANCH_NAME}" >> artifacts/build-info.txt
                    echo "Build completed at: $(date)" >> artifacts/build-info.txt
                    docker compose config > artifacts/docker-compose-config.txt
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'artifacts/*.txt', fingerprint: true
        }

        success {
            echo 'Pipeline completed successfully.'
        }

        failure {
            echo 'Pipeline failed.'
        }
    }
}