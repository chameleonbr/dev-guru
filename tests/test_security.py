"""Tests for optional API-Key security."""
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def open_client():
    """Client with no API_KEY configured (open access)."""
    with patch("src.security.settings") as mock_settings:
        mock_settings.api_key = None
        yield TestClient(app)


@pytest.fixture
def secured_client():
    """Client with API_KEY configured (protected)."""
    with patch("src.security.settings") as mock_settings:
        mock_settings.api_key = "test-secret-key-123"
        yield TestClient(app)


API_KEY = "test-secret-key-123"


# ---------------------------------------------------------------------------
# Security DISABLED (no API_KEY set)
# ---------------------------------------------------------------------------
class TestSecurityDisabled:

    def test_skills_open(self, open_client):
        resp = open_client.get("/skills")
        assert resp.status_code == 200

    def test_skills_no_header_ok(self, open_client):
        resp = open_client.get("/skills")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Security ENABLED (API_KEY set)
# ---------------------------------------------------------------------------
class TestSecurityEnabled:

    def test_skills_no_key_401(self, secured_client):
        resp = secured_client.get("/skills")
        assert resp.status_code == 401
        assert "missing" in resp.json()["detail"].lower()

    def test_skills_wrong_key_403(self, secured_client):
        resp = secured_client.get(
            "/skills", headers={"X-API-Key": "wrong-key"}
        )
        assert resp.status_code == 403
        assert "invalid" in resp.json()["detail"].lower()

    def test_skills_correct_key_200(self, secured_client):
        resp = secured_client.get(
            "/skills", headers={"X-API-Key": API_KEY}
        )
        assert resp.status_code == 200

    def test_post_skill_no_key_401(self, secured_client):
        resp = secured_client.post(
            "/skills",
            json={"url": "https://example.com/skill.zip"}
        )
        assert resp.status_code == 401

    def test_delete_skill_no_key_401(self, secured_client):
        resp = secured_client.delete("/skills/nonexistent")
        assert resp.status_code == 401

    def test_delete_skill_correct_key_404(self, secured_client):
        """Auth passes but skill doesn't exist → 404."""
        resp = secured_client.delete(
            "/skills/nonexistent",
            headers={"X-API-Key": API_KEY}
        )
        assert resp.status_code == 404
