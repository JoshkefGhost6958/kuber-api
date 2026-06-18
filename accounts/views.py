from django.conf import settings
from rest_framework.decorators import (
    api_view,
    permission_classes,
    throttle_classes,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import PassengerProfile, User
from .serializers import OtpRequestSerializer, OtpVerifySerializer, UserSerializer
from .services import OtpError, issue_otp, normalize_phone, verify_otp
from .throttles import OtpRequestThrottle


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([OtpRequestThrottle])
def otp_request(request):
    s = OtpRequestSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    try:
        code = issue_otp(s.validated_data["phone_number"])
    except ValueError as e:
        return Response({"detail": str(e)}, status=400)
    body = {"detail": "OTP sent."}
    if settings.DEBUG:
        body["dev_code"] = code
    return Response(body)


@api_view(["POST"])
@permission_classes([AllowAny])
def otp_verify(request):
    s = OtpVerifySerializer(data=request.data)
    s.is_valid(raise_exception=True)
    phone = s.validated_data["phone_number"]
    code = s.validated_data["code"]
    try:
        verify_otp(phone, code)
    except (OtpError, ValueError) as e:
        return Response({"detail": str(e)}, status=400)
    phone = normalize_phone(phone)
    user, is_new = User.objects.get_or_create(phone_number=phone)
    if is_new:
        PassengerProfile.objects.create(
            user=user, welcome_rides_remaining=settings.WELCOME_RIDES_DEFAULT
        )
    refresh = RefreshToken.for_user(user)
    return Response(
        {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data,
            "is_new": is_new,
        }
    )


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    if request.method == "PATCH":
        if "name" in request.data:
            user.name = request.data["name"]
            user.save(update_fields=["name"])
        if (
            hasattr(user, "passenger_profile")
            and "default_payment_method" in request.data
        ):
            pp = user.passenger_profile
            pp.default_payment_method = request.data["default_payment_method"]
            pp.save(update_fields=["default_payment_method"])
    return Response(UserSerializer(user).data)
