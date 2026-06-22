from rest_framework import serializers

from .models import DocumentRequirement, FareRoute, VehicleType


class FareRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = FareRoute
        fields = ["id", "origin", "destination", "price", "notes"]


class VehicleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleType
        fields = ["code", "display_name", "capacity"]


class DocumentRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentRequirement
        fields = ["doc_type", "is_mandatory"]
