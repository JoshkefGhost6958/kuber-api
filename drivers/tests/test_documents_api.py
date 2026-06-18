import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from drivers.tests.test_register_api import auth_client


@pytest.fixture(autouse=True)
def _media_tmp(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path


def driver_with_motorbike():
    c = auth_client()
    c.post("/v1/drivers/register", {"name": "Jo"}, format="json")
    c.post(
        "/v1/drivers/me/vehicles",
        {
            "vehicle_type": "MOTORBIKE",
            "make": "Boxer",
            "model": "150",
            "color": "Red",
            "year": 2021,
            "plate_number": "KMOTO1",
        },
        format="json",
    )
    return c


def image(name="id.jpg"):
    buf = io.BytesIO()
    Image.new("RGB", (2, 2), "red").save(buf, "JPEG")
    return SimpleUploadedFile(name, buf.getvalue(), content_type="image/jpeg")


@pytest.mark.django_db
def test_submit_blocked_until_mandatory_docs_present():
    c = driver_with_motorbike()
    resp = c.post("/v1/drivers/me/submit")
    assert resp.status_code == 422


@pytest.mark.django_db
def test_upload_all_then_submit_ok():
    c = driver_with_motorbike()
    for dt in ["NATIONAL_ID", "DRIVING_LICENSE", "LOGBOOK", "INSURANCE"]:
        r = c.post(
            "/v1/drivers/me/documents",
            {"doc_type": dt, "file": image(f"{dt}.jpg")},
            format="multipart",
        )
        assert r.status_code == 201
    resp = c.post("/v1/drivers/me/submit")
    assert resp.status_code == 200 and resp.json()["status"] == "UNDER_REVIEW"


@pytest.mark.django_db
def test_me_returns_checklist_with_statuses():
    c = driver_with_motorbike()
    c.post(
        "/v1/drivers/me/documents",
        {"doc_type": "NATIONAL_ID", "file": image()},
        format="multipart",
    )
    checklist = {x["doc_type"]: x["status"] for x in c.get("/v1/drivers/me").json()["checklist"]}
    assert checklist["NATIONAL_ID"] == "PENDING"
    assert checklist["DRIVING_LICENSE"] == "MISSING"
    assert "PSV_BADGE" not in checklist  # motorbike doesn't require it
