from django.conf import settings
from django.db import models


class MapMarker(models.Model):
    """An admin-placed point of interest for data collection (stages, hubs,
    demand hotspots) — surfaced on the rider/driver map."""

    class Category(models.TextChoices):
        BODA_STAGE = "BODA_STAGE", "Boda stage"
        TUKTUK_STAGE = "TUKTUK_STAGE", "Tuktuk stage"
        CAB_RANK = "CAB_RANK", "Cab rank"
        HUB = "HUB", "Hub / office"
        LANDMARK = "LANDMARK", "Landmark"
        DEMAND = "DEMAND", "Demand hotspot"
        OTHER = "OTHER", "Other"

    label = models.CharField(max_length=120)
    category = models.CharField(
        max_length=16, choices=Category.choices, default=Category.OTHER
    )
    latitude = models.FloatField()
    longitude = models.FloatField()
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.label} ({self.get_category_display()})"
