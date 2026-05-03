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
                sh 'python3 -m pip install --break-system-packages -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                sh 'python3 -m pytest --tb=short -v'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t cis4930-flask-app .'
            }
        }

        stage('Deploy with Docker Compose') {
            steps {
                sh 'docker-compose down || true'
                sh 'docker-compose up -d --build'
            }
        }

        stage('Verify Deployment Through Nginx') {
            steps {
                script {
                    // Wait for containers to be ready before probing
                    echo "Waiting for containers to initialize..."
                    sh 'sleep 5'

                    // ── Health endpoint ──────────────────────────────────────
                    echo "Checking /health endpoint..."
                    def healthPassed = false
                    for (int i = 1; i <= 5; i++) {
                        def status = sh(
                            script: 'curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health',
                            returnStdout: true
                        ).trim()
                        echo "  [Attempt ${i}/5] /health → HTTP ${status}"
                        if (status == '200') {
                            healthPassed = true
                            break
                        }
                        if (i < 5) {
                            echo "  Not ready yet — retrying in 3 s..."
                            sh 'sleep 3'
                        }
                    }
                    if (!healthPassed) {
                        error("FAILED: /health did not return 200 after 5 attempts.")
                    }
                    echo "/health check PASSED"

                    // ── Info endpoint ────────────────────────────────────────
                    echo "Checking /info endpoint..."
                    def infoPassed = false
                    for (int i = 1; i <= 5; i++) {
                        def status = sh(
                            script: 'curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/info',
                            returnStdout: true
                        ).trim()
                        echo "  [Attempt ${i}/5] /info → HTTP ${status}"
                        if (status == '200') {
                            infoPassed = true
                            break
                        }
                        if (i < 5) {
                            echo "  Not ready yet — retrying in 3 s..."
                            sh 'sleep 3'
                        }
                    }
                    if (!infoPassed) {
                        error("FAILED: /info did not return 200 after 5 attempts.")
                    }
                    echo "/info check PASSED"

                    // ── Root endpoint ────────────────────────────────────────
                    echo "Checking / (root) endpoint..."
                    def rootPassed = false
                    for (int i = 1; i <= 5; i++) {
                        def status = sh(
                            script: 'curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/',
                            returnStdout: true
                        ).trim()
                        echo "  [Attempt ${i}/5] / → HTTP ${status}"
                        if (status == '200') {
                            rootPassed = true
                            break
                        }
                        if (i < 5) {
                            echo "  Not ready yet — retrying in 3 s..."
                            sh 'sleep 3'
                        }
                    }
                    if (!rootPassed) {
                        error("FAILED: / did not return 200 after 5 attempts.")
                    }
                    echo "/ (root) check PASSED"

                    // ── Print full response bodies for logs/screenshots ──────
                    echo "=== Final response bodies ==="
                    sh 'curl -s http://localhost:8080/health'
                    sh 'curl -s http://localhost:8080/info'
                    sh 'curl -s http://localhost:8080/'
                    echo "All deployment verification checks PASSED."
                }
            }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully. All stages passed."
        }
        failure {
            echo "Pipeline failed. Check the logs above for details."
            sh 'docker-compose logs || true'
        }
        always {
            sh 'docker-compose down || true'
            echo "Cleanup complete."
        }
    }
}