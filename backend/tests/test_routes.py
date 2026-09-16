import json

def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "data" in data
    assert data["data"]["status"] == "ok"

def test_upload_document_no_file(client):
    response = client.post("/api/documents/upload")
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
    assert data["error"]["message"] == "No file provided."

def test_upload_document_empty_filename(client):
    data = {'file': (open('tests/conftest.py', 'rb'), '')}
    response = client.post('/api/documents/upload', data=data)
    assert response.status_code == 400

def test_document_not_found(client):
    response = client.get("/api/documents/9999/summary")
    assert response.status_code == 404
