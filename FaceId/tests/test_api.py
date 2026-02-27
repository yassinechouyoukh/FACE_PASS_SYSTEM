"""
tests/test_api.py
------------------
FastAPI endpoint tests using Starlette's TestClient.

The FacePipeline is mocked at import time so no models are loaded.
"""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from fastapi.testclient import TestClient


# Patch heavy imports BEFORE importing main
@pytest.fixture(scope="module")
def client():
    with (
        patch("ai.detector.yolo_face.torch"),
        patch("ai.recognizer.arcface.insightface"),
        patch("storage.database.create_engine"),
        patch("storage.database.check_db_connection", return_value=True),
        patch("app.websocket.init_pipeline"),
    ):
        from main import app

        with TestClient(app, raise_server_exceptions=True) as c:
            yield c


# ── /health ───────────────────────────────────────────────────────────────────

def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "db" in data
    assert "active_streams" in data


# ── /info ─────────────────────────────────────────────────────────────────────

def test_info_returns_metadata(client):
    response = client.get("/info")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "FacePass AiService"
    assert "version" in data
    assert "device" in data


# ── /enroll ───────────────────────────────────────────────────────────────────

@patch("main.EmbeddingRepository.save")
def test_enroll_valid(mock_save, client):
    """POST /enroll/{id} with 512-element embedding should return 200."""
    mock_record = MagicMock()
    mock_record.id = 42
    mock_save.return_value = mock_record

    embedding = list(np.random.rand(512).astype(float))
    response = client.post("/enroll/1", json=embedding)
    assert response.status_code == 200
    assert response.json()["student_id"] == 1


def test_enroll_wrong_dimension(client):
    """POST /enroll/{id} with wrong embedding size should return 422."""
    embedding = list(np.random.rand(128).astype(float))
    response = client.post("/enroll/1", json=embedding)
    assert response.status_code == 422


# ── /students/{id}/embeddings ─────────────────────────────────────────────────

@patch("main.EmbeddingRepository.get_by_student", return_value=[])
def test_list_embeddings_empty(mock_get, client):
    response = client.get("/students/99/embeddings")
    assert response.status_code == 200
    assert response.json()["count"] == 0


# ── /students/{id} DELETE ─────────────────────────────────────────────────────

@patch("main.EmbeddingRepository.delete_by_student", return_value=3)
def test_delete_student(mock_del, client):
    response = client.delete("/students/1")
    assert response.status_code == 200
    assert response.json()["deleted"] == 3
