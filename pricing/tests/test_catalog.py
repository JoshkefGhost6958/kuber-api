import pytest
from rest_framework.test import APIClient

from pricing.models import VehicleType


@pytest.mark.django_db
def test_seed_created_four_types():
    assert VehicleType.objects.filter(is_active=True).count() == 4
    assert VehicleType.objects.filter(code="BODA_ELECTRIC").exists()


@pytest.mark.django_db
def test_vehicle_types_endpoint_public():
    resp = APIClient().get("/v1/vehicle-types")
    assert resp.status_code == 200
    codes = {t["code"] for t in resp.json()}
    assert {"BODA_ELECTRIC", "BODA", "TUKTUK", "CAB"} <= codes


@pytest.mark.django_db
def test_boda_requirements_differ_from_cab():
    boda = {
        r["doc_type"]
        for r in APIClient()
        .get("/v1/drivers/document-requirements?vehicle_type=BODA_ELECTRIC")
        .json()
        if r["is_mandatory"]
    }
    cab = {
        r["doc_type"]
        for r in APIClient()
        .get("/v1/drivers/document-requirements?vehicle_type=CAB")
        .json()
        if r["is_mandatory"]
    }
    assert "PSV_BADGE" in cab
    assert "PSV_BADGE" not in boda
