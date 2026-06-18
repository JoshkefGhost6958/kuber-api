import pytest
from django.core.exceptions import ValidationError

from accounts.models import User
from drivers.models import DriverProfile


def make_driver():
    u = User.objects.create_user(
        phone_number="+254712345678", name="Jo", role=User.Role.DRIVER
    )
    return DriverProfile.objects.create(user=u)


@pytest.mark.django_db
def test_cannot_go_online_unless_approved():
    d = make_driver()
    with pytest.raises(ValidationError):
        d.go_online()


@pytest.mark.django_db
def test_submit_then_approve_then_online(monkeypatch):
    d = make_driver()
    d.submit_for_review()
    assert d.status == DriverProfile.Status.UNDER_REVIEW
    monkeypatch.setattr(d, "is_approvable", lambda: True)
    d.approve()
    assert d.status == DriverProfile.Status.APPROVED and d.approved_at
    d.go_online()
    assert d.is_online is True


@pytest.mark.django_db
def test_suspend_forces_offline(monkeypatch):
    d = make_driver()
    d.submit_for_review()
    monkeypatch.setattr(d, "is_approvable", lambda: True)
    d.approve()
    d.go_online()
    d.suspend()
    assert d.status == DriverProfile.Status.SUSPENDED and d.is_online is False


@pytest.mark.django_db
def test_approve_blocked_when_not_approvable(monkeypatch):
    d = make_driver()
    d.submit_for_review()
    monkeypatch.setattr(d, "is_approvable", lambda: False)
    with pytest.raises(ValidationError):
        d.approve()
