# CIS 4930 Cumulative Project

This project demonstrates a real-world CI/CD pipeline using multiple industry tools working together: GitHub, Jenkins, Docker, Docker Compose, Flask, Nginx, and Pytest.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Tools Used](#tools-used)
3. [Architecture](#architecture)
4. [Application Endpoints](#application-endpoints)
5. [Workflow](#workflow)
6. [Jenkins Setup](#jenkins-setup)
7. [Pipeline Stages Explained](#pipeline-stages-explained)
8. [Running the Project Locally](#running-the-project-locally)
9. [Demo Screenshots](#demo-screenshots)

---

## Project Overview

The goal of this project is to simulate a real-world DevOps pipeline where a Flask web application is automatically tested, containerized, deployed behind a reverse proxy, and verified — all triggered and orchestrated by Jenkins.

When a developer pushes code to GitHub, Jenkins picks it up, runs the full pipeline, and confirms the live application is healthy before declaring success.

---

## Tools Used

| Tool | Purpose |
|---|---|
| **GitHub** | Version control and source of truth for all project files |
| **Jenkins** | CI/CD automation — orchestrates the entire pipeline |
| **Docker** | Packages the Flask app into a reproducible container image |
| **Docker Compose** | Manages multi-container deployment (Flask + Nginx together) |
| **Flask** | Lightweight Python web application |
| **Nginx** | Reverse proxy that routes external traffic to the Flask container |
| **Pytest** | Automated test suite that runs before any deployment |

---

## Architecture

```
Client (browser / curl)
          │
          ▼
    Nginx  (host port 8080  →  container port 80)
          │
          ▼  proxy_pass
    Flask App  (container port 5000, not exposed to host)
```

Nginx is the only service with a public port. It forwards every request to the Flask container over Docker's internal network. This mirrors a production pattern where the app server is never directly reachable from the outside.

```
┌─────────────────────────────────────────────┐
│              Docker Network                 │
│                                             │
│  ┌──────────────┐     ┌──────────────────┐  │
│  │  nginx:latest│────▶│ cis4930-flask-app│  │
│  │  port 80     │     │ port 5000        │  │
│  └──────┬───────┘     └──────────────────┘  │
│         │                                   │
└─────────┼───────────────────────────────────┘
          │ host port 8080
          ▼
      Developer / Jenkins
```

---

## Application Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Home page — confirms the app is running |
| `/health` | GET | Returns `{"status": "ok"}` — used by Jenkins for deployment verification |
| `/info` | GET | Returns project metadata (name, tools used, purpose) |

---

## Workflow

```
 1. Developer pushes code to GitHub
          │
          ▼
 2. Jenkins detects the push (SCM polling or webhook)
          │
          ▼
 3. Checkout  →  pulls the latest code onto the Jenkins agent
          │
          ▼
 4. Install Dependencies  →  pip installs Flask and Pytest
          │
          ▼
 5. Run Tests  →  Pytest runs all tests in /tests
          │        if any test fails, pipeline stops here
          ▼
 6. Build Docker Image  →  docker build packages the app
          │
          ▼
 7. Deploy with Docker Compose  →  brings up Flask + Nginx containers
          │
          ▼
 8. Verify Deployment  →  curl probes /, /health, and /info through Nginx
          │                 retries up to 5 times per endpoint
          │                 prints full response bodies to the log
          ▼
 9. post { always }  →  docker-compose down cleans up containers
```

---

## Jenkins Setup

### Prerequisites

- Jenkins installed and running (locally or on a VM)
- The Jenkins agent must have installed:
  - `python3` and `pip3`
  - `docker` and `docker compose` (the agent user must be in the `docker` group)
  - `curl`
- A GitHub repository containing this project

### Connecting Jenkins to GitHub

1. Open Jenkins → **New Item** → **Pipeline** → give it a name → OK.
2. Under **Pipeline**, set **Definition** to `Pipeline script from SCM`.
3. Set **SCM** to `Git` and paste your repository URL.
4. Set **Branch Specifier** to `*/main` (or whichever branch you use).
5. Set **Script Path** to `Jenkinsfile`.
6. Save.

### Triggering the Pipeline

**Option A — Manual run:**  
Click **Build Now** in the Jenkins job to run the pipeline immediately.

**Option B — SCM Polling (recommended for local Jenkins):**  
Under **Build Triggers**, enable **Poll SCM** and set the schedule to `H/5 * * * *` (checks every 5 minutes).

**Option C — GitHub Webhook (requires Jenkins reachable from GitHub):**  
Under **Build Triggers**, enable **GitHub hook trigger for GITScm polling**. Then add a webhook in your GitHub repo settings pointing to `http://<your-jenkins-url>/github-webhook/`.

---

## Pipeline Stages Explained

### Stage 1 — Checkout
```groovy
checkout scm
```
Jenkins pulls the latest commit from the configured GitHub branch onto the agent workspace. This is the starting point for every run.

### Stage 2 — Install Dependencies
```groovy
sh 'python3 -m pip install --break-system-packages -r requirements.txt'
```
Installs `flask` and `pytest` directly on the agent. The `--break-system-packages` flag is required on newer Ubuntu/Debian systems where pip is managed by the OS.

### Stage 3 — Run Tests
```groovy
sh 'python3 -m pytest --tb=short -v'
```
Runs the full Pytest suite in `/tests`. The `-v` flag prints each test name and result. The `--tb=short` flag prints a concise traceback on failure. **If any test fails, the pipeline stops here and never touches Docker.** This is the safety gate.

### Stage 4 — Build Docker Image
```groovy
sh 'docker build -t cis4930-flask-app .'
```
Builds a Docker image from the `Dockerfile` in the repo root and tags it `cis4930-flask-app`. The image packages the app and all dependencies into a portable, reproducible unit.

### Stage 5 — Deploy with Docker Compose
```groovy
sh 'docker-compose down || true'
sh 'docker-compose up -d --build'
```
First tears down any previous containers (the `|| true` prevents failure if nothing is running). Then brings up both the `flask-app` and `nginx` containers in detached mode. Nginx is wired to forward requests to the Flask container over Docker's internal network.

### Stage 6 — Verify Deployment Through Nginx *(Thom's stage)*
```groovy
script {
    sh 'sleep 5'
    // retry loop for /health, /info, and /
}
```
This is the deployment verification stage. Rather than a single blind `curl` call, it:

- **Waits 5 seconds** after `docker-compose up` so containers have time to initialize before the first probe.
- **Checks three endpoints** — `/health`, `/info`, and `/` — each through Nginx on port 8080.
- **Retries up to 5 times** per endpoint with a 3-second delay between attempts, printing the HTTP status code on every attempt so the Jenkins log shows exactly what happened.
- **Fails fast** with a descriptive error message if any endpoint never returns 200.
- **Prints the full response bodies** of all three endpoints at the end so the Jenkins log serves as a screenshot-ready proof of a live, correct deployment.

### Post Actions
```groovy
post {
    success  { echo "Pipeline completed successfully." }
    failure  { sh 'docker-compose logs || true' }
    always   { sh 'docker-compose down || true' }
}
```
- On **success**: logs a confirmation message.
- On **failure**: dumps `docker-compose logs` to help diagnose what went wrong.
- **Always**: tears down the containers so the host stays clean between runs.

---

## Running the Project Locally

### Without Jenkins (manual test)

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd <repo-folder>

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Run tests
pytest -v

# 4. Start the stack
docker-compose up -d --build

# 5. Verify manually
curl http://localhost:8080/health
curl http://localhost:8080/info
curl http://localhost:8080/

# 6. Tear down
docker-compose down
```

### With Jenkins (full pipeline)

1. Make sure Jenkins is running: `http://localhost:8080` (default Jenkins port — if Nginx is also on 8080, adjust Jenkins to another port such as 9090).
2. Create the pipeline job as described in [Jenkins Setup](#jenkins-setup).
3. Click **Build Now**.
4. Open **Console Output** to watch each stage in real time.
5. A green checkmark means all stages passed including deployment verification.

---

## Demo Screenshots

> *(Replace the placeholders below with actual screenshots when running the pipeline.)*

| What to capture | Where to find it |
|---|---|
| Pytest passing | Jenkins Console Output — Stage: Run Tests |
| Docker Compose starting | Jenkins Console Output — Stage: Deploy with Docker Compose |
| Verification retry loop + HTTP 200s | Jenkins Console Output — Stage: Verify Deployment Through Nginx |
| Full response bodies (`/health`, `/info`, `/`) | Bottom of the Verify stage output |
| Green pipeline overview | Jenkins job page → Stage View |

---

*Project for CIS 4930 — DevOps toolchain demonstration.*