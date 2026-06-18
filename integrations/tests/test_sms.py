from integrations.sms import FakeSmsProvider, SmsProvider, get_sms_provider


def test_fake_records_sent():
    FakeSmsProvider.sent.clear()
    p = FakeSmsProvider()
    p.send_otp("+254712345678", "123456")
    assert FakeSmsProvider.sent[-1] == ("+254712345678", "123456")


def test_get_sms_provider_returns_instance():
    assert isinstance(get_sms_provider(), SmsProvider)
