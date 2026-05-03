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
                bat 'pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                bat 'python -m pytest --tb=short -v'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t cis4930-flask-app .'
            }
        }

        stage('Deploy with Docker Compose') {
            steps {
                bat 'docker compose down || exit 0'
                bat 'docker compose up -d --build'
            }
        }

        stage('Verify Deployment Through Nginx') {
            steps {
                script {
                    echo "Waiting for containers to initialize..."
                    sleep(time: 5, unit: 'SECONDS')

                    // ── Health endpoint ──────────────────────────────────────
                    echo "Checking /health endpoint..."
                    def healthPassed = false
                    for (int i = 1; i <= 5; i++) {
                        def result = bat(
                            script: 'curl -s -o NUL -w "%%{http_code}" http://localhost:8081/health',
                            returnStdout: true
                        ).trim()
                        def status = result.readLines().last().trim()
                        echo "  [Attempt ${i}/5] /health → HTTP ${status}"
                        if (status == '200') {
                            healthPassed = true
                            break
                        }
                        if (i < 5) {
                            echo "  Not ready yet — retrying in 3s..."
                            sleep(time: 3, unit: 'SECONDS')
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
                        def result = bat(
                            script: 'curl -s -o NUL -w "%%{http_code}" http://localhost:8081/info',
                            returnStdout: true
                        ).trim()
                        def status = result.readLines().last().trim()
                        echo "  [Attempt ${i}/5] /info → HTTP ${status}"
                        if (status == '200') {
                            infoPassed = true
                            break
                        }
                        if (i < 5) {
                            echo "  Not ready yet — retrying in 3s..."
                            sleep(time: 3, unit: 'SECONDS')
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
                        def result = bat(
                            script: 'curl -s -o NUL -w "%%{http_code}" http://localhost:8081/',
                            returnStdout: true
                        ).trim()
                        def status = result.readLines().last().trim()
                        echo "  [Attempt ${i}/5] / → HTTP ${status}"
                        if (status == '200') {
                            rootPassed = true
                            break
                        }
                        if (i < 5) {
                            echo "  Not ready yet — retrying in 3s..."
                            sleep(time: 3, unit: 'SECONDS')
                        }
                    }
                    if (!rootPassed) {
                        error("FAILED: / did not return 200 after 5 attempts.")
                    }
                    echo "/ (root) check PASSED"

                    // ── Print full response bodies for logs/screenshots ──────
                    echo "=== Final response bodies ==="
                    bat 'curl -s http://localhost:8081/health'
                    bat 'curl -s http://localhost:8081/info'
                    bat 'curl -s http://localhost:8081/'
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
            bat 'docker compose logs || exit 0'
        }
        always {
            // bat 'docker compose down || exit 0' screenshot purpose
            echo "Cleanup complete."
        }
    }
}