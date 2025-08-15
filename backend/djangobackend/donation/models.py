from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from datetime import timedelta, datetime
import hashlib  # For faster OTP hashing

# Admin model
class Admin1(models.Model):
    first_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.first_name


class Registration(models.Model):
    name = models.CharField(max_length=50, verbose_name="Full Name")
    email = models.EmailField(unique=True, verbose_name="Email Address")
    password = models.CharField(max_length=128)

    otp_code = models.CharField(max_length=128, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    last_otp_sent_at = models.DateTimeField(null=True, blank=True)  # For rate-limiting
    is_verified = models.BooleanField(default=False)


    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def check_password(self, raw_password):
        """Check if the provided password matches the stored password"""
        return check_password(raw_password, self.password)

    def set_otp(self, raw_otp):
        # Rate-limiting: Allow OTP resend only after 1 minute
        if self.last_otp_sent_at and (timezone.now() < self.last_otp_sent_at + timedelta(minutes=1)):
            raise ValueError("Wait 1 minute before requesting a new OTP.")
        
        self.otp_code = hashlib.sha256(raw_otp.encode()).hexdigest()  # Faster than make_password()
        self.otp_created_at = timezone.now()
        self.last_otp_sent_at = timezone.now()
        self.save()

    def verify_otp(self, raw_otp, expiry_minutes=5):
        if not self.otp_code:
            return False, "OTP not set"
        if timezone.now() > self.otp_created_at + timedelta(minutes=expiry_minutes):
            return False, "OTP expired"
        if hashlib.sha256(raw_otp.encode()).hexdigest() == self.otp_code:  # Compare hashes
            self.is_verified = True
            self.otp_code = None
            self.otp_created_at = None
            self.save()
            return True, "Verified"
        return False, "Invalid OTP"

    class Meta:
        verbose_name = "User Registration"
        verbose_name_plural = "User Registrations"



class login(models.Model):
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)  # after OTP verification

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['']  # keep username optional if not needed

    def __str__(self):
        return self.email


class OTP(models.Model):
    user = models.ForeignKey(login, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)  # 5 min expiry

    def __str__(self):
        return f"{self.user.email} - {self.code}"