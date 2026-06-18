from django.contrib.auth.models import BaseUserManager

from .services import normalize_phone


class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra):
        if not phone_number:
            raise ValueError("phone_number is required")
        user = self.model(phone_number=normalize_phone(phone_number), **extra)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("is_active", True)
        extra.setdefault("name", "Admin")
        return self.create_user(phone_number, password, **extra)
