from rest_framework import serializers

from .models import MapMarker


class MapMarkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = MapMarker
        fields = ["id", "label", "category", "latitude", "longitude", "notes"]
