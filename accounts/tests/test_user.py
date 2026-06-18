import pytest

from accounts.models import User
from accounts.services import normalize_phone


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("0712345678", "+254712345678"),
        ("254712345678", "+254712345678"),
        ("+254712345678", "+254712345678"),
        (" 0712 345 678 ", "+254712345678"),
    ],
)
def test_normalize_phone(raw, expected):
    assert normalize_phone(raw) == expected


def test_normalize_phone_invalid():
    with pytest.raises(ValueError):
        normalize_phone("hello")


@pytest.mark.django_db
def test_create_user_defaults_passenger():
    u = User.objects.create_user(phone_number="+254712345678", name="Ada")
    assert u.role == User.Role.PASSENGER
    assert u.is_active and not u.is_staff
