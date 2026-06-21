import pytest

from drivers.tests.test_register_api import auth_client


def driver_client():
    c = auth_client()
    c.post("/v1/drivers/register", {"name": "Jo"}, format="json")
    return c


PLATE = "KDB123X"


@pytest.mark.django_db
def test_add_motorbike():
    c = driver_client()
    resp = c.post(
        "/v1/drivers/me/vehicles",
        {
            "vehicle_type": "BODA_ELECTRIC",
            "make": "Boxer",
            "model": "150",
            "color": "Red",
            "year": 2021,
            "plate_number": PLATE,
        },
        format="json",
    )
    assert resp.status_code == 201
    assert resp.json()["vehicle_type"] == "BODA_ELECTRIC"
    assert resp.json()["is_active"] is True  # first vehicle auto-active


@pytest.mark.django_db
def test_activating_second_deactivates_first():
    c = driver_client()
    v1 = c.post(
        "/v1/drivers/me/vehicles",
        {
            "vehicle_type": "BODA",
            "make": "Vitz",
            "model": "F",
            "color": "White",
            "year": 2018,
            "plate_number": "KAA111A",
        },
        format="json",
    ).json()
    v2 = c.post(
        "/v1/drivers/me/vehicles",
        {
            "vehicle_type": "CAB",
            "make": "Fielder",
            "model": "G",
            "color": "Silver",
            "year": 2019,
            "plate_number": "KBB222B",
        },
        format="json",
    ).json()
    c.patch(f"/v1/drivers/me/vehicles/{v2['id']}", {"is_active": True}, format="json")
    listing = {v["id"]: v["is_active"] for v in c.get("/v1/drivers/me/vehicles").json()}
    assert listing[v2["id"]] is True and listing[v1["id"]] is False
