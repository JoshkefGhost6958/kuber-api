import abc

from django.conf import settings
from django.utils.module_loading import import_string


class SmsProvider(abc.ABC):
    @abc.abstractmethod
    def send_otp(self, phone: str, code: str) -> None:
        ...


class FakeSmsProvider(SmsProvider):
    """Dev/test provider — records sent codes instead of dispatching SMS."""

    sent: list[tuple[str, str]] = []

    def send_otp(self, phone: str, code: str) -> None:
        self.sent.append((phone, code))


def get_sms_provider() -> SmsProvider:
    return import_string(settings.SMS_PROVIDER)()
