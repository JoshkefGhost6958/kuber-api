from django.db import migrations

TYPES = [
    ("MOTORBIKE", "Boda", 1),
    ("MINI", "Mini", 3),
    ("STANDARD", "Standard", 4),
    ("XL", "XL", 6),
]
CAR_DOCS = [
    "NATIONAL_ID",
    "DRIVING_LICENSE",
    "PSV_BADGE",
    "LOGBOOK",
    "INSPECTION_CERT",
    "INSURANCE",
]
MOTO_DOCS = ["NATIONAL_ID", "DRIVING_LICENSE", "LOGBOOK", "INSURANCE"]


def seed(apps, schema_editor):
    VT = apps.get_model("pricing", "VehicleType")
    DR = apps.get_model("pricing", "DocumentRequirement")
    for code, name, cap in TYPES:
        vt, _ = VT.objects.get_or_create(
            code=code, defaults={"display_name": name, "capacity": cap}
        )
        docs = MOTO_DOCS if code == "MOTORBIKE" else CAR_DOCS
        for d in docs:
            DR.objects.get_or_create(
                vehicle_type=vt, doc_type=d, defaults={"is_mandatory": True}
            )


def unseed(apps, schema_editor):
    apps.get_model("pricing", "VehicleType").objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [("pricing", "0001_initial")]
    operations = [migrations.RunPython(seed, unseed)]
