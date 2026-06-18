import pytest
from rest_framework.test import APIClient

from pricing.models import VehicleType


@pytest.mark.django_db
def test_seed_created_four_types():
    assert VehicleType.objects.filter(is_active=True).count() == 4
    assert VehicleType.objects.filter(code="MOTORBIKE").exists()


@pytest.mark.django_db
def test_vehicle_types_endpoint_public():
    resp = APIClient().get("/v1/vehicle-types")
    assert resp.status_code == 200
    codes = {t["code"] for t in resp.json()}
    assert {"MOTORBIKE", "MINI", "STANDARD", "XL"} <= codes


@pytest.mark.django_db
def test_motorbike_requirements_differ_from_car():
    moto = {
        r["doc_type"]
        for r in APIClient()
        .get("/v1/drivers/document-requirements?vehicle_type=MOTORBIKE")
        .json()
        if r["is_mandatory"]
    }
    car = {
        r["doc_type"]
        for r in APIClient()
        .get("/v1/drivers/document-requirements?vehicle_type=STANDARD")
        .json()
        if r["is_mandatory"]
    }
    assert "PSV_BADGE" in car
    assert "PSV_BADGE" not in moto
