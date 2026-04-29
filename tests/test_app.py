from app import app


def test_home():
    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 200
    assert b"Flask app is running" in response.data


def test_health():
    client = app.test_client()
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_info():
    client = app.test_client()
    response = client.get("/info")

    assert response.status_code == 200

    data = response.get_json()
    assert data["project"] == "CIS 4930 Cumulative Project"
    assert "Jenkins" in data["tools"]
    assert "Docker" in data["tools"]
    assert "Flask" in data["tools"]