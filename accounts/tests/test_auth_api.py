import pytest
from rest_framework.test import APIClient

from accounts.models import PassengerProfile, User


@pytest.mark.django_db
def test_otp_request_returns_dev_code_in_debug():
    resp = APIClient().post(
        "/v1/auth/otp/request", {"phone_number": "0712345678"}, format="json"
    )
    assert resp.status_code == 200
    assert len(resp.json()["dev_code"]) == 6


@pytest.mark.django_db
def test_verify_creates_passenger_and_returns_tokens():
    c = APIClient()
    code = c.post(
        "/v1/auth/otp/request", {"phone_number": "0712345678"}, format="json"
    ).json()["dev_code"]
    resp = c.post(
        "/v1/auth/otp/verify",
        {"phone_number": "0712345678", "code": code},
        format="json",
    )
    body = resp.json()
    assert resp.status_code == 200
    assert body["is_new"] is True
    assert body["user"]["role"] == "PASSENGER"
    assert "access" in body and "refresh" in body
    user = User.objects.get(phone_number="+254712345678")
    assert PassengerProfile.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_verify_existing_user_is_not_new():
    c = APIClient()
    body = None
    for _ in range(2):
        code = c.post(
            "/v1/auth/otp/request", {"phone_number": "0712345678"}, format="json"
        ).json()["dev_code"]
        body = c.post(
            "/v1/auth/otp/verify",
            {"phone_number": "0712345678", "code": code},
            format="json",
        ).json()
    assert body["is_new"] is False


@pytest.mark.django_db
def test_verify_bad_code_400():
    c = APIClient()
    c.post("/v1/auth/otp/request", {"phone_number": "0712345678"}, format="json")
    resp = c.post(
        "/v1/auth/otp/verify",
        {"phone_number": "0712345678", "code": "000000"},
        format="json",
    )
    assert resp.status_code == 400
