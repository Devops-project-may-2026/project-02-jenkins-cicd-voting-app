pipeline {
    agent any

    environment {
        DOCKER_USER = 'marta77784'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                sh '''
                    GIT_SHA=$(git rev-parse --short HEAD)
                    docker build -t ${DOCKER_USER}/voting-vote:${GIT_SHA} -t ${DOCKER_USER}/voting-vote:latest ./vote
                    docker build -t ${DOCKER_USER}/voting-result:${GIT_SHA} -t ${DOCKER_USER}/voting-result:latest ./result
                    docker build --platform linux/amd64 -t ${DOCKER_USER}/voting-worker:${GIT_SHA} -t ${DOCKER_USER}/voting-worker:latest ./worker
                '''
            }
        }

        stage('Push') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                    sh '''
                        GIT_SHA=$(git rev-parse --short HEAD)
                        echo ${DOCKER_PASSWORD} | docker login -u ${DOCKER_USERNAME} --password-stdin
                        docker push ${DOCKER_USER}/voting-vote:${GIT_SHA}
                        docker push ${DOCKER_USER}/voting-vote:latest
                        docker push ${DOCKER_USER}/voting-result:${GIT_SHA}
                        docker push ${DOCKER_USER}/voting-result:latest
                        docker push ${DOCKER_USER}/voting-worker:${GIT_SHA}
                        docker push ${DOCKER_USER}/voting-worker:latest
                        docker logout
                    '''
                }
            }
        }
    }

    post {
        always {
            sh '''
                GIT_SHA=$(git rev-parse --short HEAD)
                mkdir -p artifacts
                echo "Build: ${BUILD_NUMBER}" > artifacts/build-info.txt
                echo "Git SHA: ${GIT_SHA}" >> artifacts/build-info.txt
                echo "Published images:" >> artifacts/build-info.txt
                echo "  marta77784/voting-vote:${GIT_SHA}" >> artifacts/build-info.txt
                echo "  marta77784/voting-result:${GIT_SHA}" >> artifacts/build-info.txt
                echo "  marta77784/voting-worker:${GIT_SHA}" >> artifacts/build-info.txt
                echo "marta77784/voting-vote:${GIT_SHA}" > artifacts/images.txt
                echo "marta77784/voting-result:${GIT_SHA}" >> artifacts/images.txt
                echo "marta77784/voting-worker:${GIT_SHA}" >> artifacts/images.txt
            '''
            archiveArtifacts artifacts: 'artifacts/**', allowEmptyArchive: true
        }
    }
}