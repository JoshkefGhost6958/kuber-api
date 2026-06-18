from rest_framework.throttling import SimpleRateThrottle


class OtpRequestThrottle(SimpleRateThrottle):
    """Throttle OTP requests per phone number (falling back to client IP).

    Rate comes from DEFAULT_THROTTLE_RATES["otp_request"] in settings.
    """

    scope = "otp_request"

    def get_cache_key(self, request, view):
        ident = request.data.get("phone_number") or self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ident}
