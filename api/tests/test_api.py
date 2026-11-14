from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    assert client.get("/").status_code == 200

def test_health():
    assert client.get("/api/v1/health").json()["status"] == "ok"

def test_seed_catalog():
    response = client.get("/api/v1/songs")
    assert response.status_code == 200
    assert response.json()["count"] >= 1

def test_appearance():
    response = client.get("/api/v1/songs/demo-space-song/appearance")
    assert response.status_code == 200
    assert len(response.json()["palette"]) == 3
