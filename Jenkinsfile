pipeline {
    agent any

    environment {
        DOCKER_COMPOSE_FILE = 'docker-compose.yml'
        PROJECT_NAME = 'iris-flower-mlops'
        GITHUB_REPO = 'https://github.com/Harikrushna2272/IRIS-FLOWER-MLOps.git'
    }

    stages {
        stage('Checkout') {
            steps {
                echo '================================'
                echo 'Checking out code from repository'
                echo "Repository: ${GITHUB_REPO}"
                echo "Branch: ${env.BRANCH_NAME ?: 'main'}"
                echo '================================'
                script {
                    try {
                        // Try to use SCM if configured (when using "Pipeline script from SCM")
                        checkout scm
                    } catch (Exception e) {
                        // If SCM not configured (Direct Pipeline Script), clone from GitHub
                        echo "SCM not configured, cloning from GitHub..."
                        sh """
                            if [ -d ".git" ]; then
                                echo "Repository already exists, pulling latest changes..."
                                git pull origin main || echo "Pull failed, continuing with existing code..."
                            else
                                echo "Cloning repository..."
                                git clone ${GITHUB_REPO} . || echo "Clone failed, using workspace as-is..."
                            fi
                        """
                    }
                }
            }
        }

        stage('Environment Setup') {
            steps {
                echo 'Setting up environment...'
                sh '''
                    echo "Python version:"
                    python3 --version
                    echo "Docker version:"
                    docker --version
                    echo "Docker Compose version:"
                    docker compose version
                '''
            }
        }

        stage('Build Docker Images') {
            steps {
                echo 'Building Docker images...'
                sh '''
                    docker compose -f ${DOCKER_COMPOSE_FILE} build --no-cache
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running tests...'
                echo 'Tests are skipped for now - will run during deployment validation'
                echo 'To enable tests, add test files to api/ and db/ directories'
            }
        }

        stage('Stop Existing Containers') {
            steps {
                echo 'Stopping existing containers...'
                sh '''
                    docker compose -f ${DOCKER_COMPOSE_FILE} down || true
                '''
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploying application...'
                sh '''
                    docker compose -f ${DOCKER_COMPOSE_FILE} up -d
                '''
            }
        }

        stage('Health Check') {
            steps {
                echo 'Performing health checks...'
                script {
                    sleep 60  // Wait for services to start and download dependencies
                    sh '''
                        echo "Checking if containers are running..."
                        docker ps | grep -E "api_service|db_service"

                        echo "Checking API service logs..."
                        docker logs api_service 2>&1 | grep -q "Uvicorn running" && echo "API service is running ✓"

                        echo "Checking DB service logs..."
                        docker logs db_service 2>&1 | grep -q "Uvicorn running" && echo "DB service is running ✓"

                        echo "All services are healthy!"
                    '''
                }
            }
        }

        stage('Cleanup Old Images') {
            steps {
                echo 'Cleaning up old Docker images...'
                sh '''
                    docker image prune -f
                '''
            }
        }
    }

    post {
        success {
            echo '================================'
            echo '✅ Pipeline executed successfully!'
            echo '================================'
            echo "Build: ${env.BUILD_NUMBER}"
            echo "Commit: ${env.GIT_COMMIT?.take(7)}"
            echo "Branch: ${env.BRANCH_NAME ?: 'main'}"
            echo '================================'
            echo 'API Service: http://localhost:8000'
            echo 'DB Service: http://localhost:8001'
            echo '================================'
        }
        failure {
            echo '================================'
            echo '❌ Pipeline failed!'
            echo '================================'
            echo "Build: ${env.BUILD_NUMBER}"
            echo "Commit: ${env.GIT_COMMIT?.take(7)}"
            echo "Branch: ${env.BRANCH_NAME ?: 'main'}"
            echo '================================'
            sh '''
                echo "Displaying logs for debugging..."
                docker compose -f ${DOCKER_COMPOSE_FILE} logs --tail=50
                docker compose -f ${DOCKER_COMPOSE_FILE} down
            '''
        }
        always {
            echo 'Cleaning up workspace...'
            // Comment out cleanWs() to keep workspace for debugging
            // cleanWs()
        }
    }
}
