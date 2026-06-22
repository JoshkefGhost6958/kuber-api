import re
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone


def normalize_phone(raw: str) -> str:
    """Normalize a Kenyan phone number to E.164 (+254XXXXXXXXX)."""
    digits = re.sub(r"[\s\-()]", "", raw or "")
    if digits.startswith("+254") and len(digits) == 13 and digits[1:].isdigit():
        return digits
    if digits.startswith("254") and len(digits) == 12 and digits.isdigit():
        return "+" + digits
    if digits.startswith("0") and len(digits) == 10 and digits.isdigit():
        return "+254" + digits[1:]
    raise ValueError(f"Invalid Kenyan phone number: {raw!r}")


class OtpError(Exception):
    pass


def issue_otp(phone: str, purpose: str = "LOGIN") -> str:
    """Generate a 6-digit OTP, persist it hashed, send via the SMS provider."""
    from integrations.sms import get_sms_provider

    from .models import OtpCode

    phone = normalize_phone(phone)
    code = f"{secrets.randbelow(1_000_000):06d}"
    OtpCode.objects.create(
        phone_number=phone,
        code_hash=make_password(code),
        purpose=purpose,
        expires_at=timezone.now() + timedelta(seconds=settings.OTP_TTL_SECONDS),
    )
    get_sms_provider().send_otp(phone, code)
    return code


def verify_otp(phone: str, code: str, purpose: str = "LOGIN") -> bool:
    """Verify an OTP. Consumes on success; raises OtpError otherwise.

    On a wrong guess, increments attempts; once attempts reach
    OTP_MAX_ATTEMPTS the code is locked and the user must request a new one.
    """
    from .models import OtpCode

    phone = normalize_phone(phone)
    # Demo/master OTP bypass (env-gated) — lets testers sign in without SMS.
    if settings.DEMO_OTP and code == settings.DEMO_OTP:
        return True
    otp = (
        OtpCode.objects.filter(
            phone_number=phone, purpose=purpose, consumed_at__isnull=True
        )
        .order_by("-created_at")
        .first()
    )
    if otp is None or otp.is_expired:
        raise OtpError("No valid code. Request a new one.")
    if otp.attempts >= settings.OTP_MAX_ATTEMPTS:
        raise OtpError("Too many attempts. Request a new code.")
    if not check_password(code, otp.code_hash):
        otp.attempts += 1
        otp.save(update_fields=["attempts"])
        raise OtpError("Incorrect code.")
    otp.consumed_at = timezone.now()
    otp.save(update_fields=["consumed_at"])
    return True
