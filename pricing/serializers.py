from rest_framework import serializers

from .models import DocumentRequirement, VehicleType


class VehicleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleType
        fields = ["code", "display_name", "capacity"]


class DocumentRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentRequirement
        fields = ["doc_type", "is_mandatory"]
