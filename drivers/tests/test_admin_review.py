import pytest
from django.core.exceptions import ValidationError

from accounts.models import User
from drivers.models import ComplianceDocument, DriverProfile, Vehicle
from pricing.models import VehicleType


@pytest.mark.django_db
def test_full_approval_flow():
    u = User.objects.create_user(
        phone_number="+254700000000", name="D", role=User.Role.DRIVER
    )
    d = DriverProfile.objects.create(user=u)
    moto = VehicleType.objects.get(code="MOTORBIKE")
    Vehicle.objects.create(
        driver=d,
        vehicle_type=moto,
        make="B",
        model="1",
        color="R",
        year=2020,
        plate_number="KX1",
        is_active=True,
    )
    for dt in ["NATIONAL_ID", "DRIVING_LICENSE", "LOGBOOK", "INSURANCE"]:
        ComplianceDocument.objects.create(driver=d, doc_type=dt, file="compliance/x.jpg")
    d.submit_for_review()
    with pytest.raises(ValidationError):  # docs still PENDING
        d.approve()
    for doc in d.documents.all():
        doc.approve(by=u)
    d.approve()
    assert d.status == DriverProfile.Status.APPROVED
