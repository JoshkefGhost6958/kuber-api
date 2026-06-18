import pytest
from django.conf import settings

from accounts.services import OtpError, issue_otp, verify_otp
from integrations.sms import FakeSmsProvider


@pytest.mark.django_db
def test_issue_and_verify():
    FakeSmsProvider.sent.clear()
    code = issue_otp("0712345678")
    assert FakeSmsProvider.sent[-1] == ("+254712345678", code)
    assert verify_otp("0712345678", code) is True


@pytest.mark.django_db
def test_wrong_code_counts_attempts_then_locks():
    issue_otp("+254712345678")
    for _ in range(settings.OTP_MAX_ATTEMPTS):
        with pytest.raises(OtpError):
            verify_otp("+254712345678", "000000")
    # further attempts still raise (locked), even with a right-looking code
    with pytest.raises(OtpError):
        verify_otp("+254712345678", "000000")


@pytest.mark.django_db
def test_code_single_use():
    code = issue_otp("+254712345678")
    assert verify_otp("+254712345678", code) is True
    with pytest.raises(OtpError):
        verify_otp("+254712345678", code)
