from django.db import migrations

# Target-market taxonomy: electric boda, petrol boda, tuktuk (carrier), cab.
TYPES = [
    ("BODA_ELECTRIC", "Boda (Electric)", 1),
    ("BODA", "Boda", 1),
    ("TUKTUK", "Tuktuk", 3),
    ("CAB", "Cab", 4),
]
BODA_DOCS = ["NATIONAL_ID", "DRIVING_LICENSE", "LOGBOOK", "INSURANCE"]
PSV_DOCS = [
    "NATIONAL_ID",
    "DRIVING_LICENSE",
    "PSV_BADGE",
    "LOGBOOK",
    "INSPECTION_CERT",
    "INSURANCE",
]


def retaxonomy(apps, schema_editor):
    VT = apps.get_model("pricing", "VehicleType")
    DR = apps.get_model("pricing", "DocumentRequirement")
    Vehicle = apps.get_model("drivers", "Vehicle")

    # Vehicles PROTECT their VehicleType; clear them (dev/seed data) before reset.
    Vehicle.objects.all().delete()
    DR.objects.all().delete()
    VT.objects.all().delete()

    for code, name, cap in TYPES:
        vt = VT.objects.create(code=code, display_name=name, capacity=cap)
        docs = BODA_DOCS if code in ("BODA_ELECTRIC", "BODA") else PSV_DOCS
        for d in docs:
            DR.objects.create(vehicle_type=vt, doc_type=d, is_mandatory=True)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("pricing", "0002_seed"),
        ("drivers", "0003_compliancedocument"),
    ]
    operations = [migrations.RunPython(retaxonomy, noop)]
