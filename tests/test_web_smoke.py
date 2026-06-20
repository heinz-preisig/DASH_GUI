"""
Smoke tests for the web applications.

Uses the Flask test_client so the apps do not need to bind real ports.
Verifies that both Brick and Schema web UIs render and their core APIs answer.
"""

import pytest

from brick_app.api.web_api import BrickWebAPI
from brick_app.core.multi_tenant_backend import MultiTenantBackend as BrickBackend
from schema_app.interfaces.web.flask_app import SchemaWebAPI
from schema_app.core.multi_tenant_backend import MultiTenantBackend as SchemaBackend


@pytest.fixture
def brick_client():
    backend = BrickBackend()
    api = BrickWebAPI(backend, host="localhost", port=5000)
    with api.app.test_client() as client:
        yield client


@pytest.fixture
def schema_client():
    backend = SchemaBackend()
    api = SchemaWebAPI(backend, host="localhost", port=5001)
    with api.app.test_client() as client:
        yield client


def test_brick_app_index_renders(brick_client):
    response = brick_client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Brick App v2" in html
    assert "data-presets=\"react\"" in html


def test_brick_app_enrichment_boolean(brick_client):
    response = brick_client.get("/api/enrichment/datatype?datatype=xsd:boolean")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "success"
    assert payload["data"]["widget"] == "boolean_toggle"


def test_schema_app_index_renders(schema_client):
    response = schema_client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Schema App v2" in html


def test_schema_app_health(schema_client):
    response = schema_client.get("/api/health")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "success"
    assert "timestamp" in payload["data"]
