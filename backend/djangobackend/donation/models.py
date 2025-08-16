from django.db import models
from django.contrib.auth.models import  BaseUserManager
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from django.db.models.functions import Lower
import random
import hashlib

class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True")
        return self.create_user(email, name, password, **extra_fields)


class UserModel(models.Model):
    name = models.CharField(max_length=50, verbose_name="Full Name")
    email = models.EmailField(unique=True, verbose_name="Email Address")
    password = models.CharField(max_length=128)

    # OTP fields
    otp_code = models.CharField(max_length=128, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)

    # Auth/flags
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)  # must be True to login
    is_staff = models.BooleanField(default=False)  # required for admin access

    created_at = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'   # login with email
    REQUIRED_FIELDS = ['name']  # required when creating superuser

    class Meta:
        constraints = [
            models.UniqueConstraint(Lower("email"), name="uniq_user_email_ci")
        ]
        indexes = [
            models.Index(Lower("email"), name="idx_user_email_ci"),
        ]

    def __str__(self):
        return self.email

    # --- OTP helpers ---
    def set_otp(self) -> str:
        raw_otp = f"{random.randint(100000, 999999)}"
        self.otp_code = hashlib.sha256(raw_otp.encode()).hexdigest()
        self.otp_created_at = timezone.now()
        self.save(update_fields=["otp_code", "otp_created_at"])
        return raw_otp

    def verify_otp(self, otp: str):
        if not self.otp_code:
            return False, "OTP not found"
        if not self.otp_created_at or (timezone.now() - self.otp_created_at).total_seconds() > 600:
            self.otp_code = None
            self.otp_created_at = None
            self.save(update_fields=["otp_code", "otp_created_at"])
            return False, "OTP expired"
        if hashlib.sha256(otp.encode()).hexdigest() == self.otp_code:
            self.is_verified = True
            self.is_active = True
            self.otp_code = None
            self.otp_created_at = None
            self.save(update_fields=["is_verified", "is_active", "otp_code", "otp_created_at"])
            return True, "Verified"
        return False, "Invalid OTP"
