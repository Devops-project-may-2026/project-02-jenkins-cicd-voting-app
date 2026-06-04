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

        stage('Structure Validation') {
            steps {
                echo 'Validating project structure...'
                // TODO: replace with real unit/integration tests in Epic 4
                sh 'test -f docker-compose.yml'
                sh 'test -d vote'
                sh 'test -d result'
                sh 'test -d worker'
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

        stage('Trivy Security Scan Reports') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                    echo 'Running Trivy scans and saving reports...'
                    sh '''
                        mkdir -p trivy-reports

                        for service in vote result worker; do
                            image=${DOCKER_USERNAME}/voting-${service}:latest
                            echo "Scanning image: $image"
                            docker run --rm \
                                -v /var/run/docker.sock:/var/run/docker.sock \
                                -v "$WORKSPACE/trivy-reports:/reports" \
                                aquasec/trivy:latest image \
                                --severity HIGH,CRITICAL \
                                --format table \
                                --exit-code 0 \
                                -o /reports/${service}-trivy-report.txt \
                                $image
                        done
                    '''
                }
            }
        }

        stage('Trivy Security Gate') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                    echo 'Enforcing security gate: fail on HIGH or CRITICAL vulnerabilities...'
                    sh '''
                        for service in vote result worker; do
                            image=${DOCKER_USERNAME}/voting-${service}:latest
                            echo "Checking security gate for image: $image"
                            docker run --rm \
                                -v /var/run/docker.sock:/var/run/docker.sock \
                                aquasec/trivy:latest image \
                                --severity HIGH,CRITICAL \
                                --exit-code 1 \
                                $image
                        done
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
            archiveArtifacts artifacts: 'trivy-reports/*.txt', fingerprint: true, allowEmptyArchive: true
        }

        success {
            echo 'Pipeline completed successfully.'
        }

        failure {
            echo 'Pipeline failed.'
        }
    }
}