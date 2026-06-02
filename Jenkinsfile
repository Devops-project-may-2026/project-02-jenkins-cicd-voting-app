pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                    sh '''
                        GIT_SHA=$(git rev-parse --short HEAD)
                        docker build -t ${DOCKER_USERNAME}/voting-vote:${GIT_SHA} -t ${DOCKER_USERNAME}/voting-vote:latest ./vote
                        docker build -t ${DOCKER_USERNAME}/voting-result:${GIT_SHA} -t ${DOCKER_USERNAME}/voting-result:latest ./result
                        docker build --platform linux/amd64 -t ${DOCKER_USERNAME}/voting-worker:${GIT_SHA} -t ${DOCKER_USERNAME}/voting-worker:latest ./worker
                    '''
                }
            }
        }

        stage('Push') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                    sh '''
                        GIT_SHA=$(git rev-parse --short HEAD)
                        echo ${DOCKER_PASSWORD} | docker login -u ${DOCKER_USERNAME} --password-stdin
                        docker push ${DOCKER_USERNAME}/voting-vote:${GIT_SHA}
                        docker push ${DOCKER_USERNAME}/voting-vote:latest
                        docker push ${DOCKER_USERNAME}/voting-result:${GIT_SHA}
                        docker push ${DOCKER_USERNAME}/voting-result:latest
                        docker push ${DOCKER_USERNAME}/voting-worker:${GIT_SHA}
                        docker push ${DOCKER_USERNAME}/voting-worker:latest
                        docker logout
                    '''
                }
            }
        }
    }

    post {
        always {
            withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                sh '''
                    GIT_SHA=$(git rev-parse --short HEAD)
                    mkdir -p artifacts
                    echo "Build: ${BUILD_NUMBER}" > artifacts/build-info.txt
                    echo "Git SHA: ${GIT_SHA}" >> artifacts/build-info.txt
                    echo "Published images:" >> artifacts/build-info.txt
                    echo "  ${DOCKER_USERNAME}/voting-vote:${GIT_SHA}" >> artifacts/build-info.txt
                    echo "  ${DOCKER_USERNAME}/voting-result:${GIT_SHA}" >> artifacts/build-info.txt
                    echo "  ${DOCKER_USERNAME}/voting-worker:${GIT_SHA}" >> artifacts/build-info.txt
                    echo "${DOCKER_USERNAME}/voting-vote:${GIT_SHA}" > artifacts/images.txt
                    echo "${DOCKER_USERNAME}/voting-result:${GIT_SHA}" >> artifacts/images.txt
                    echo "${DOCKER_USERNAME}/voting-worker:${GIT_SHA}" >> artifacts/images.txt
                '''
            }
            archiveArtifacts artifacts: 'artifacts/**', allowEmptyArchive: true
        }
    }
}