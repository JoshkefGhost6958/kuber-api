from rest_framework import serializers

from pricing.models import VehicleType

from .models import DriverProfile, Vehicle


class DriverProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverProfile
        fields = ["status", "rejection_reason", "is_online"]


class VehicleSerializer(serializers.ModelSerializer):
    vehicle_type = serializers.SlugRelatedField(
        slug_field="code", queryset=VehicleType.objects.all()
    )

    class Meta:
        model = Vehicle
        fields = [
            "id",
            "vehicle_type",
            "make",
            "model",
            "color",
            "year",
            "plate_number",
            "is_active",
        ]
        read_only_fields = ["is_active"]
