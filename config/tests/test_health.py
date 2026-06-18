import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_health_ok():
    resp = APIClient().get("/v1/health/")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
