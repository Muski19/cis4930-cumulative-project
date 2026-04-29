# CIS 4930 Cumulative Project

This project demonstrates a simple DevOps workflow using multiple industry tools working together, including Jenkins, Docker, Flask, and Nginx.

## Project Overview

The goal of this project is to simulate a real-world CI/CD pipeline where a Flask application is automatically tested, containerized, deployed, and verified using Jenkins.

## Tools Used

- GitHub (version control)
- Jenkins (CI/CD automation)
- Docker (containerization)
- Docker Compose (multi-container deployment)
- Flask (web application)
- Nginx (reverse proxy)
- Pytest (automated testing)

---

## Application Endpoints

- `/` → Home page
- `/health` → Returns application health status
- `/info` → Returns project metadata

---

## Workflow

The automated workflow is as follows:

1. Code is pushed to GitHub
2. Jenkins pulls the repository
3. Jenkins installs dependencies
4. Jenkins runs automated tests using pytest
5. Jenkins builds a Docker image for the Flask app
6. Jenkins deploys the application using Docker Compose
7. Nginx routes incoming requests to the Flask container
8. Jenkins verifies deployment by calling `/health` endpoint

---

## Architecture

```text
Client (browser/curl)
        ↓
     Nginx (port 8080)
        ↓
     Flask App (port 5000)
```