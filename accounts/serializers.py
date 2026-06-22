from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "phone_number", "name", "role", "is_staff"]
        read_only_fields = ["is_staff"]


class OtpRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField()


class OtpVerifySerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    code = serializers.CharField()
