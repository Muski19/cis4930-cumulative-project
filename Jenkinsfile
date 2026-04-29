pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                sh 'pytest'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t cis4930-flask-app .'
            }
        }

        stage('Deploy with Docker Compose') {
            steps {
                sh 'docker compose down || true'
                sh 'docker compose up -d --build'
            }
        }

        stage('Verify Deployment Through Nginx') {
            steps {
                sh '''
                for i in 1 2 3 4 5; do
                    curl -f http://localhost:8080/health && exit 0
                    echo "Waiting for app through Nginx..."
                    sleep 2
                done
                exit 1
                '''
            }
        }
    }

    post {
        always {
            sh 'docker compose down || true'
        }
    }
}