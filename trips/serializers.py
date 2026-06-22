from rest_framework import serializers

from .models import Trip


class TripSerializer(serializers.ModelSerializer):
    driver = serializers.SerializerMethodField()
    passenger_name = serializers.SerializerMethodField()
    vehicle_type = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = [
            "id",
            "status",
            "origin_label",
            "dest_label",
            "origin_lat",
            "origin_lng",
            "dest_lat",
            "dest_lng",
            "vehicle_type",
            "payment_method",
            "base_fare",
            "client_fee",
            "driver_fee",
            "client_total",
            "driver_payout",
            "platform_cut",
            "status",
            "created_at",
            "accepted_at",
            "driver",
            "passenger_name",
        ]

    def get_vehicle_type(self, t):
        return t.vehicle_type.code if t.vehicle_type else None

    def get_passenger_name(self, t):
        return t.passenger.name

    def get_driver(self, t):
        d = t.driver
        if not d:
            return None
        v = d.vehicles.filter(is_active=True).first()
        return {
            "name": d.user.name,
            "phone": d.user.phone_number,
            "vehicle_type": v.vehicle_type.code if v else None,
            "vehicle": f"{v.make} {v.model}" if v else None,
            "plate": v.plate_number if v else None,
            "lat": d.current_lat,
            "lng": d.current_lng,
            "rating_avg": str(d.rating_avg) if d.rating_avg is not None else None,
        }
