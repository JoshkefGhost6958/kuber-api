from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from accounts.models import User
from pricing.models import VehicleType


class DriverProfile(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        UNDER_REVIEW = "UNDER_REVIEW", "Under review"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        SUSPENDED = "SUSPENDED", "Suspended"

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="driver_profile"
    )
    status = models.CharField(
        max_length=14, choices=Status.choices, default=Status.PENDING
    )
    rejection_reason = models.TextField(blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    is_online = models.BooleanField(default=False)
    current_lat = models.FloatField(null=True, blank=True)
    current_lng = models.FloatField(null=True, blank=True)
    last_location_at = models.DateTimeField(null=True, blank=True)
    rating_avg = models.DecimalField(
        max_digits=3, decimal_places=2, null=True, blank=True
    )
    rating_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Driver {self.user.phone_number} ({self.status})"

    def is_approvable(self) -> bool:
        from .services import is_driver_approvable

        return is_driver_approvable(self)

    def submit_for_review(self):
        if self.status not in (self.Status.PENDING, self.Status.REJECTED):
            raise ValidationError("Can only submit from PENDING or REJECTED.")
        self.status = self.Status.UNDER_REVIEW
        self.rejection_reason = ""
        self.save(update_fields=["status", "rejection_reason"])

    def approve(self):
        if self.status not in (self.Status.UNDER_REVIEW, self.Status.SUSPENDED):
            raise ValidationError("Can only approve from UNDER_REVIEW or SUSPENDED.")
        if not self.is_approvable():
            raise ValidationError("Mandatory documents are not all approved.")
        self.status = self.Status.APPROVED
        self.approved_at = timezone.now()
        self.save(update_fields=["status", "approved_at"])

    def reject(self, reason: str):
        if self.status != self.Status.UNDER_REVIEW:
            raise ValidationError("Can only reject from UNDER_REVIEW.")
        self.status = self.Status.REJECTED
        self.rejection_reason = reason
        self.save(update_fields=["status", "rejection_reason"])

    def suspend(self):
        if self.status != self.Status.APPROVED:
            raise ValidationError("Can only suspend an APPROVED driver.")
        self.status = self.Status.SUSPENDED
        self.is_online = False
        self.save(update_fields=["status", "is_online"])

    def go_online(self):
        if self.status != self.Status.APPROVED:
            raise ValidationError("Only APPROVED drivers can go online.")
        self.is_online = True
        self.save(update_fields=["is_online"])

    def go_offline(self):
        self.is_online = False
        self.save(update_fields=["is_online"])


class Vehicle(models.Model):
    driver = models.ForeignKey(
        DriverProfile, on_delete=models.CASCADE, related_name="vehicles"
    )
    vehicle_type = models.ForeignKey(
        VehicleType, on_delete=models.PROTECT, related_name="vehicles"
    )
    make = models.CharField(max_length=40)
    model = models.CharField(max_length=40)
    color = models.CharField(max_length=20)
    year = models.PositiveIntegerField()
    plate_number = models.CharField(max_length=12, unique=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.plate_number} ({self.vehicle_type.code})"


class ComplianceDocument(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    driver = models.ForeignKey(
        DriverProfile, on_delete=models.CASCADE, related_name="documents"
    )
    doc_type = models.CharField(max_length=20)
    file = models.ImageField(upload_to="compliance/")
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    reviewed_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("driver", "doc_type")]

    def __str__(self):
        return f"{self.driver.user.phone_number}:{self.doc_type} ({self.status})"

    def approve(self, by):
        self.status = self.Status.APPROVED
        self.reviewed_by = by
        self.reviewed_at = timezone.now()
        self.rejection_reason = ""
        self.save(
            update_fields=["status", "reviewed_by", "reviewed_at", "rejection_reason"]
        )

    def reject(self, by, reason):
        self.status = self.Status.REJECTED
        self.reviewed_by = by
        self.reviewed_at = timezone.now()
        self.rejection_reason = reason
        self.save(
            update_fields=["status", "reviewed_by", "reviewed_at", "rejection_reason"]
        )
