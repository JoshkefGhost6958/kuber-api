from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        PASSENGER = "PASSENGER", "Passenger"
        DRIVER = "DRIVER", "Driver"

    phone_number = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=120, blank=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.PASSENGER)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"{self.name or 'User'} ({self.phone_number})"


class OtpCode(models.Model):
    class Purpose(models.TextChoices):
        LOGIN = "LOGIN", "Login"
        WITHDRAWAL = "WITHDRAWAL", "Withdrawal"
        PHONE_CHANGE = "PHONE_CHANGE", "Phone change"

    phone_number = models.CharField(max_length=16, db_index=True)
    code_hash = models.CharField(max_length=128)
    purpose = models.CharField(
        max_length=16, choices=Purpose.choices, default=Purpose.LOGIN
    )
    expires_at = models.DateTimeField()
    attempts = models.PositiveIntegerField(default=0)
    consumed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["phone_number", "purpose"])]

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at
