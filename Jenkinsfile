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

        stage('Build Docker Images') {
            steps {
                echo 'Building application services with Docker Compose...'
                sh 'docker compose build vote result worker'
            }
        }

        stage('Structure Validation') {
            steps {
                echo 'Running basic project structure validation...'
                // TODO: replace with real unit/integration tests in a future epic
                sh 'test -f docker-compose.yml'
                sh 'test -d vote'
                sh 'test -d result'
                sh 'test -d worker'
            }
        }

        stage('Trivy Security Scan Reports') {
            steps {
                echo 'Running Trivy scans and saving reports...'
                sh '''
                    mkdir -p trivy-reports

                    for image in \
                        project-02-jenkins-cicd-voting-app-vote:latest \
                        project-02-jenkins-cicd-voting-app-result:latest \
                        project-02-jenkins-cicd-voting-app-worker:latest
                    do
                        report_name=$(echo "$image" | sed 's/project-02-jenkins-cicd-voting-app-//; s/:latest//')

                        echo "Scanning image: $image"

                        docker run --rm \
                            -v /var/run/docker.sock:/var/run/docker.sock \
                            -v "$WORKSPACE/trivy-reports:/reports" \
                            aquasec/trivy:latest image \
                            --severity HIGH,CRITICAL \
                            --format table \
                            --exit-code 0 \
                            -o /reports/${report_name}-trivy-report.txt \
                            $image
                    done
                '''
            }
        }

        stage('Trivy Security Gate') {
            steps {
                echo 'Enforcing security gate: fail on HIGH or CRITICAL vulnerabilities...'
                sh '''
                    for image in \
                        project-02-jenkins-cicd-voting-app-vote:latest \
                        project-02-jenkins-cicd-voting-app-result:latest \
                        project-02-jenkins-cicd-voting-app-worker:latest
                    do
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
            archiveArtifacts artifacts: 'artifacts/*.txt', fingerprint: true, allowEmptyArchive: true
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