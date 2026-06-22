from django.db import models

from accounts.models import User
from drivers.models import DriverProfile
from pricing.models import VehicleType


class Trip(models.Model):
    class Status(models.TextChoices):
        REQUESTED = "REQUESTED", "Requested"
        ACCEPTED = "ACCEPTED", "Accepted"
        ARRIVING = "ARRIVING", "Driver arriving"
        ARRIVED = "ARRIVED", "Driver arrived"
        IN_PROGRESS = "IN_PROGRESS", "In progress"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    class Payment(models.TextChoices):
        MPESA = "MPESA", "M-Pesa"
        CASH = "CASH", "Cash"

    passenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name="trips")
    driver = models.ForeignKey(
        DriverProfile, null=True, blank=True, on_delete=models.SET_NULL, related_name="trips"
    )

    origin_label = models.CharField(max_length=160)
    dest_label = models.CharField(max_length=160)
    origin_lat = models.FloatField(null=True, blank=True)
    origin_lng = models.FloatField(null=True, blank=True)
    dest_lat = models.FloatField(null=True, blank=True)
    dest_lng = models.FloatField(null=True, blank=True)

    vehicle_type = models.ForeignKey(
        VehicleType, null=True, blank=True, on_delete=models.SET_NULL, related_name="trips"
    )
    payment_method = models.CharField(
        max_length=6, choices=Payment.choices, default=Payment.MPESA
    )

    # Fare breakdown (KSh) — null when the route isn't mapped yet.
    base_fare = models.PositiveIntegerField(null=True, blank=True)
    client_fee = models.PositiveIntegerField(default=0)
    driver_fee = models.PositiveIntegerField(default=0)
    client_total = models.PositiveIntegerField(null=True, blank=True)
    driver_payout = models.PositiveIntegerField(null=True, blank=True)
    platform_cut = models.PositiveIntegerField(null=True, blank=True)

    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.REQUESTED
    )
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["status", "created_at"])]
        ordering = ["-created_at"]

    def __str__(self):
        return f"Trip #{self.pk} {self.origin_label}->{self.dest_label} ({self.status})"
