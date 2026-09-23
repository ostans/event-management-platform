from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

phone_regex = RegexValidator(
    regex=r"^\+989\d{9}$",
    message="Phone number must be in the format: +989XXXXXXXXX",
)


class CustomUserManager(BaseUserManager):

    def _create_user(self, phone_number, password=None, **extra_fields):
        first_name = extra_fields.get("first_name")
        last_name = extra_fields.get("last_name")
        if not phone_number:
            raise ValueError("The E field must be set")
        if not first_name or not last_name:
            raise ValueError("The Fullname fiel must be set")
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_active", True)
        return self._create_user(phone, password, **extra_fields)

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_active") is not True:
            raise ValueError("Superuser must have is_active=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    class Role(models.TextChoices):
        ORGANIZER = "organizer", "Organizer"
        PARTICIPANT = "participant", "Participant"
        STAFF = "staff", "Staff"

    phone_number = models.CharField(max_length=13, unique=True, validators=[phone_regex])
    first_name = models.CharField()
    last_name = models.CharField()
    role = models.CharField(max_length=11, choices=Role.choices, default=Role.PARTICIPANT)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.first_name} - {self.last_name}"
