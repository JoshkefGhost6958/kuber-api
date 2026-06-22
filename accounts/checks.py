from django.conf import settings
from django.core.checks import Error, register


@register()
def demo_otp_requires_allowlist(app_configs, **kwargs):
    """A demo OTP without an allowlist would be a master credential for every
    account — refuse that configuration outright."""
    if settings.DEMO_OTP and not settings.DEMO_PHONES:
        return [
            Error(
                "DEMO_OTP is set but DEMO_PHONES is empty — that is a master OTP "
                "for every account.",
                hint="Set DEMO_PHONES to an allowlist of test numbers, or unset DEMO_OTP.",
                id="accounts.E001",
            )
        ]
    return []
