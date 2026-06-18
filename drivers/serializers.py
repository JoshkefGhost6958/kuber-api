from rest_framework import serializers

from pricing.models import VehicleType

from .models import ComplianceDocument, DriverProfile, Vehicle


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


class ComplianceDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplianceDocument
        fields = [
            "id",
            "doc_type",
            "file",
            "status",
            "rejection_reason",
            "expiry_date",
            "uploaded_at",
        ]
        read_only_fields = ["status", "rejection_reason", "uploaded_at"]
