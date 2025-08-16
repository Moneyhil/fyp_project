from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from datetime import timedelta
import random
import hashlib  # For faster OTP hashing

class User(models.Model):
    name = models.CharField(max_length=50, verbose_name="Full Name")
    email = models.EmailField(unique=True, verbose_name="Email Address")
    password = models.CharField(max_length=128)
    otp_code = models.CharField(max_length=128, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def check_password(self, raw_password):
        """Check if the provided password matches the stored password"""
        return check_password(raw_password, self.password)

    def set_otp(self):
        # Generate a 6-digit OTP
        raw_otp = f"{random.randint(100000, 999999)}"
        
        # Hash the OTP for storage
        hashed_otp = hashlib.sha256(raw_otp.encode()).hexdigest()
        
        # Store the hashed OTP and timestamp
        self.otp_code = hashed_otp
        self.otp_created_at = timezone.now()
        self.save()
        
        return raw_otp

    def verify_otp(self, otp):
        # Check if OTP exists
        if not self.otp_code:
            return False, "OTP not found"
        
        # Check if OTP is expired (10 minutes)
        time_difference = timezone.now() - self.otp_created_at
        if time_difference.total_seconds() > 600:  # 10 minutes
            self.otp_code = None
            self.otp_created_at = None
            self.save()
            return False, "OTP expired"
        
        # Verify OTP
        if hashlib.sha256(otp.encode()).hexdigest() == self.otp_code:
            # Mark as verified and clear OTP
            self.is_verified = True
            self.otp_code = None
            self.otp_created_at = None
            self.save()
            return True, "Verified"
        
        return False, "Invalid OTP"