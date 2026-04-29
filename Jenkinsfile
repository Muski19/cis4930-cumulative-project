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

        stage('Run Container') {
            steps {
                sh 'docker rm -f cis4930-flask-app || true'
                sh 'docker run -d --name cis4930-flask-app -p 5000:5000 cis4930-flask-app'
            }
        }

        stage('Verify Deployment') {
            steps {
                sh 'curl -f http://localhost:5000/health'
            }
        }
    }

    post {
        always {
            sh 'docker rm -f cis4930-flask-app || true'
        }
    }
}