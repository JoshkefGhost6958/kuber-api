from django.db import models


class VehicleType(models.Model):
    class Code(models.TextChoices):
        BODA_ELECTRIC = "BODA_ELECTRIC", "Boda (Electric)"
        BODA = "BODA", "Boda"
        TUKTUK = "TUKTUK", "Tuktuk"
        CAB = "CAB", "Cab"

    code = models.CharField(max_length=16, choices=Code.choices, unique=True)
    display_name = models.CharField(max_length=32)
    capacity = models.PositiveSmallIntegerField(default=4)
    base_fare = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    per_km_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=1)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.display_name


class DocumentRequirement(models.Model):
    class DocType(models.TextChoices):
        NATIONAL_ID = "NATIONAL_ID", "National ID"
        DRIVING_LICENSE = "DRIVING_LICENSE", "Driving license"
        PSV_BADGE = "PSV_BADGE", "PSV badge"
        LOGBOOK = "LOGBOOK", "Logbook"
        INSPECTION_CERT = "INSPECTION_CERT", "Inspection certificate"
        INSURANCE = "INSURANCE", "Insurance"

    vehicle_type = models.ForeignKey(
        VehicleType, on_delete=models.CASCADE, related_name="requirements"
    )
    doc_type = models.CharField(max_length=20, choices=DocType.choices)
    is_mandatory = models.BooleanField(default=True)

    class Meta:
        unique_together = [("vehicle_type", "doc_type")]

    def __str__(self):
        return f"{self.vehicle_type.code}:{self.doc_type}"


class FareRoute(models.Model):
    """Driver-collected flat fare between two named places (KSh).

    Origin/destination are matched case-insensitively (contains), so e.g.
    origin "Mbuni" covers "Mbuni Hostel". Populated by ops/field staff as
    drivers report stage-to-stage prices.
    """

    origin = models.CharField(max_length=120)
    destination = models.CharField(max_length=120)
    price = models.PositiveIntegerField(help_text="Flat fare in KSh")
    vehicle_type = models.ForeignKey(
        VehicleType,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="fares",
        help_text="Optional; blank = applies to any vehicle (e.g. boda).",
    )
    notes = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["origin", "destination"])]

    def __str__(self):
        return f"{self.origin} → {self.destination}: KSh {self.price}"
