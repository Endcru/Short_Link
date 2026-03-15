from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_main_endpoints():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Short Link service"}

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy / здоров", "database": "connected / подключена", "architecture": "DDD with async SQLAlchemy 2.0"}

    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")

def test_main_endpoints_invalid():
    response = client.get("/wrong_endpoint")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}