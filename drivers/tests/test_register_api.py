import pytest
from rest_framework.test import APIClient

from accounts.models import User
from drivers.models import DriverProfile


def auth_client(phone="0712345678"):
    c = APIClient()
    code = c.post(
        "/v1/auth/otp/request", {"phone_number": phone}, format="json"
    ).json()["dev_code"]
    tok = c.post(
        "/v1/auth/otp/verify", {"phone_number": phone, "code": code}, format="json"
    ).json()["access"]
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {tok}")
    return c


@pytest.mark.django_db
def test_register_makes_driver():
    c = auth_client()
    resp = c.post("/v1/drivers/register", {"name": "Jo Driver"}, format="json")
    assert resp.status_code == 200
    assert resp.json()["status"] == "PENDING"
    u = User.objects.get(phone_number="+254712345678")
    assert u.role == User.Role.DRIVER and hasattr(u, "driver_profile")


@pytest.mark.django_db
def test_register_idempotent():
    c = auth_client()
    c.post("/v1/drivers/register", {"name": "Jo"}, format="json")
    resp = c.post("/v1/drivers/register", {"name": "Jo"}, format="json")
    assert resp.status_code == 200
    assert DriverProfile.objects.count() == 1
