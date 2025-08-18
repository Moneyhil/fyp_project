from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models.functions import Lower
import secrets
import hashlib
import datetime

class UserManager(BaseUserManager):
    def _validate_email(self, email):
        """Validate email format."""
        try:
            validate_email(email)
            return True
        except ValidationError:
            return False

    def create_user(self, email, name, password=None, **extra_fields):
        """
        Creates and saves a User with the given email, name and password.
        """
        if not email:
            raise ValueError(_('Users must have an email address'))
        
        if not self._validate_email(email):
            raise ValueError(_('Invalid email format'))
            
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            name=name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given email, name and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
            
        return self.create_user(email, name, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that uses email as the unique identifier 
    instead of username, with OTP verification support.
    """
    name = models.CharField(_('Full Name'), max_length=150)
    email = models.EmailField(_('Email Address'), unique=True)
    
    # Verification fields
    otp_secret = models.CharField(max_length=128, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    otp_expires_at = models.DateTimeField(null=True, blank=True)
    
    # Status flags
    is_verified = models.BooleanField(_('Verified'), default=False)
    is_active = models.BooleanField(_('Active'), default=True)
    is_staff = models.BooleanField(_('Staff status'), default=False)
    
    # Timestamps
    date_joined = models.DateTimeField(_('Date joined'), auto_now_add=True)
    last_login = models.DateTimeField(_('Last login'), null=True, blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        constraints = [
            models.UniqueConstraint(
                Lower('email'),
                name='unique_user_email_ci'
            )
        ]
        indexes = [
            models.Index(Lower('email'), name='idx_user_email_ci'),
        ]

    def __str__(self):
        return self.email

    def clean(self):
        """Normalize and validate model before saving."""
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def generate_otp(self, expiry_minutes=10):
        """
        Generates a time-based OTP and stores its hash.
        Returns the raw OTP code for sending to user.
        """
        raw_otp = ''.join(secrets.choice('0123456789') for _ in range(6))
        self.otp_secret = hashlib.sha256(raw_otp.encode()).hexdigest()
        self.otp_created_at = timezone.now()
        self.otp_expires_at = self.otp_created_at + datetime.timedelta(minutes=expiry_minutes)
        self.save(update_fields=['otp_secret', 'otp_created_at', 'otp_expires_at'])
        return raw_otp

    def verify_otp(self, otp):
        """
        Verifies the provided OTP against the stored hash.
        Returns tuple of (success: bool, message: str).
        """
        if not self.otp_secret or not self.otp_expires_at:
            return False, _('No OTP request found')
            
        if timezone.now() > self.otp_expires_at:
            self.clear_otp()
            return False, _('OTP has expired')
            
        if hashlib.sha256(otp.encode()).hexdigest() != self.otp_secret:
            return False, _('Invalid OTP code')
            
        self.is_verified = True
        self.is_active = True
        self.clear_otp()
        self.save(update_fields=['is_verified', 'is_active', 'otp_secret', 'otp_created_at', 'otp_expires_at'])
        return True, _('Verification successful')

    def clear_otp(self):
        """Clears any existing OTP data."""
        self.otp_secret = None
        self.otp_created_at = None
        self.otp_expires_at = None


class Profile(models.Model):
    """
    User profile model to store additional user information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(
        _('First Name'), 
        max_length=50, 
        blank=True, 
        null=True,
        help_text='Enter your first name (max 50 characters)'
    )
    last_name = models.CharField(
        _('Last Name'), 
        max_length=50, 
        blank=True, 
        null=True,
        help_text='Enter your last name (max 50 characters)'
    )
    contact_number = models.CharField(
        _('Contact Number'), 
        max_length=15, 
        blank=True, 
        null=True,
        help_text='Enter a valid contact number (max 15 digits)'
    )
    address = models.TextField(
        _('Address'), 
        blank=True, 
        null=True,
        help_text='Enter your complete address'
    )
    gender = models.CharField(
        _('Gender'), 
        max_length=10, 
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other')
        ], 
        blank=True, 
        null=True,
        help_text='Select your gender'
    )
    city = models.CharField(
        _('City'), 
        max_length=50, 
        blank=True, 
        null=True,
        help_text='Enter your city name (max 50 characters)'
    )
    blood_group = models.CharField(
        _('Blood Group'), 
        max_length=5, 
        choices=[
            ('A+', 'A+'),
            ('A-', 'A-'),
            ('B+', 'B+'),
            ('B-', 'B-'),
            ('O+', 'O+'),
            ('O-', 'O-'),
            ('AB+', 'AB+'),
            ('AB-', 'AB-')
        ], 
        blank=True, 
        null=True,
        help_text='Select your blood group'
    )
    role = models.CharField(
        _('Role'), 
        max_length=10, 
        choices=[
            ('donor', 'Donor'),
            ('needer', 'Needer')
        ], 
        blank=True, 
        null=True,
        help_text='Select your role - Donor or Needer'
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')
    
    def clean(self):
        """Custom validation for the Profile model."""
        from django.core.exceptions import ValidationError
        import re
        
        # Validate contact number format
        if self.contact_number:
            # Remove spaces and check if it contains only digits
            clean_number = self.contact_number.replace(' ', '').replace('-', '')
            if not re.match(r'^[0-9]{11}$', clean_number):
                raise ValidationError({
                    'contact_number': 'Contact number must be exactly 11 numeric digits'
                })
        
        # Validate name fields don't contain numbers or special characters
        if self.first_name:
            if not re.match(r'^[a-zA-Z\s]+$', self.first_name):
                raise ValidationError({
                    'first_name': 'First name should only contain letters and spaces'
                })
        
        if self.last_name:
            if not re.match(r'^[a-zA-Z\s]+$', self.last_name):
                raise ValidationError({
                    'last_name': 'Last name should only contain letters and spaces'
                })
        
        # Validate city name
        if self.city:
            if not re.match(r'^[a-zA-Z\s]+$', self.city):
                raise ValidationError({
                    'city': 'City name should only contain letters and spaces'
                })
    
    def save(self, *args, **kwargs):
        """Override save to call clean validation."""
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.email} - Profile"
    
    @property
    def full_name(self):
        """Returns the full name of the user."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or self.user.name