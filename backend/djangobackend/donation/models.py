from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models.functions import Lower
from django.db.models.signals import post_save
from django.dispatch import receiver
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
        super().clean()
        if self.email:
            self.email = self.email.lower()

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


class Admin(models.Model):
    """
    Admin model to store admin accounts separately from regular users.
    """
    name = models.CharField(_('Full Name'), max_length=150)
    email = models.EmailField(_('Email Address'), unique=True)
    password = models.CharField(_('Password'), max_length=128)
    
    # Status flags
    is_active = models.BooleanField(_('Active'), default=True)
    is_superuser = models.BooleanField(_('Superuser'), default=False)
    
    # Timestamps
    date_joined = models.DateTimeField(_('Date joined'), auto_now_add=True)
    last_login = models.DateTimeField(_('Last login'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Admin')
        verbose_name_plural = _('Admins')
        constraints = [
            models.UniqueConstraint(
                Lower('email'),
                name='unique_admin_email_ci'
            )
        ]
        indexes = [
            models.Index(Lower('email'), name='idx_admin_email_ci'),
        ]

    def __str__(self):
        return self.email

    def clean(self):
        """Normalize and validate model before saving."""
        super().clean()
        if self.email:
            self.email = self.email.lower()
    
    def set_password(self, raw_password):
        """Hash and set the password."""
        from django.contrib.auth.hashers import make_password
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        """Check if the provided password matches the stored hash."""
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password)


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
        choices=[
            ('Sheikhupura', 'Sheikhupura'),
            ('Lahore', 'Lahore'),
            ('Islamabad', 'Islamabad'),
            ('Faisalabad', 'Faisalabad')
        ],
        blank=True, 
        null=True,
        help_text='Select your city'
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


class DonationRequest(models.Model):
    """
    Model to track blood donation requests between users (needers) and donors.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('user_accepted', 'User Accepted'),
        ('donor_accepted', 'Donor Accepted'),
        ('both_accepted', 'Both Accepted'),
        ('user_declined', 'User Declined'),
        ('donor_declined', 'Donor Declined'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    requester = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='donation_requests_made',
        help_text='User who needs blood'
    )
    donor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='donation_requests_received',
        help_text='Donor who can provide blood'
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
        help_text='Required blood group'
    )
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text='Current status of the donation request'
    )
    user_response = models.BooleanField(
        _('User Response'),
        null=True,
        blank=True,
        help_text='True if user accepts, False if declines, None if no response'
    )
    donor_response = models.BooleanField(
        _('Donor Response'),
        null=True,
        blank=True,
        help_text='True if donor accepts, False if declines, None if no response'
    )
    # urgency_level field removed
    notes = models.TextField(
        _('Notes'),
        blank=True,
        null=True,
        help_text='Additional notes or comments about the donation request'
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    expires_at = models.DateTimeField(
        _('Expires At'),
        null=True,
        blank=True,
        help_text='When this request expires'
    )
    
    class Meta:
        verbose_name = _('Donation Request')
        verbose_name_plural = _('Donation Requests')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['requester', 'status']),
            models.Index(fields=['donor', 'status']),
            models.Index(fields=['blood_group', 'status']),
        ]
    
    def __str__(self):
        return f"Request from {self.requester.name} to {self.donor.name} for {self.blood_group}"
    
    def update_status(self):
        """Update status based on user and donor responses."""
        if self.user_response is True and self.donor_response is True:
            self.status = 'both_accepted'
        elif self.user_response is True and self.donor_response is None:
            self.status = 'user_accepted'
        elif self.user_response is None and self.donor_response is True:
            self.status = 'donor_accepted'
        elif self.user_response is False:
            self.status = 'user_declined'
        elif self.donor_response is False:
            self.status = 'donor_declined'
        else:
            self.status = 'pending'
        self.save()





class CallLog(models.Model):
    """
    Model to track call logs between users and donors.
    """
    CALL_STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('answered', 'Answered'),
        ('completed', 'Completed'),
        ('missed', 'Missed'),
        ('declined', 'Declined'),
    ]
    
    caller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='calls_made',
        help_text='User who initiated the call'
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='calls_received',
        help_text='User who received the call'
    )
    # Remove this field since it was already removed in migration 0009
    # donation_request = models.ForeignKey(
    #     'DonationRequest',
    #     on_delete=models.CASCADE,
    #     related_name='call_logs',
    #     help_text='The donation request this call is related to'
    # )
    call_status = models.CharField(
        _('Call Status'),
        max_length=20,
        choices=CALL_STATUS_CHOICES,
        default='initiated',
        help_text='Current status of the call'
    )
    duration_seconds = models.PositiveIntegerField(
        _('Duration (seconds)'),
        null=True,
        blank=True,
        help_text='Duration of the call in seconds'
    )
    caller_confirmed = models.BooleanField(
        _('Caller Confirmed'),
        default=False,
        help_text='Whether caller confirmed the call completion'
    )
    receiver_confirmed = models.BooleanField(
        _('Receiver Confirmed'),
        default=False,
        help_text='Whether receiver confirmed the call completion'
    )
    both_confirmed = models.BooleanField(
        _('Both Confirmed'),
        default=False,
        help_text='Whether both parties confirmed the call'
    )
    # Email confirmation fields
    email_sent = models.BooleanField(
        _('Email Sent'),
        default=False,
        help_text='Whether confirmation email was sent to donor'
    )
    email_sent_at = models.DateTimeField(
        _('Email Sent At'),
        null=True,
        blank=True,
        help_text='When the confirmation email was sent'
    )
    donor_email_response = models.CharField(
        _('Donor Email Response'),
        max_length=10,
        choices=[
            ('pending', 'Pending'),
            ('yes', 'Yes - Agreed to Donate'),
            ('no', 'No - Declined to Donate'),
        ],
        default='pending',
        help_text='Donor response from email confirmation'
    )
    email_response_at = models.DateTimeField(
        _('Email Response At'),
        null=True,
        blank=True,
        help_text='When donor responded via email'
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Call Log')
        verbose_name_plural = _('Call Logs')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['caller', 'call_status']),
            models.Index(fields=['receiver', 'call_status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Call from {self.caller.name} to {self.receiver.name} - {self.call_status}"
    
    def mark_both_confirmed(self):
        """Mark call as confirmed by both parties."""
        if self.caller_confirmed and self.receiver_confirmed:
            self.both_confirmed = True
            self.call_status = 'completed'
            self.save()


class MonthlyDonationTracker(models.Model):
    """
    Model to track monthly donation goals and completed calls.
    Tracks when 3 confirmed calls complete a monthly count.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='monthly_trackers',
        help_text='User whose monthly donations are being tracked'
    )
    month = models.DateField(
        _('Month'),
        help_text='Month being tracked (YYYY-MM-01 format)'
    )
    completed_calls_count = models.PositiveIntegerField(
        _('Completed Calls Count'),
        default=0,
        help_text='Number of confirmed calls completed this month'
    )
    monthly_goal_completed = models.BooleanField(
        _('Monthly Goal Completed'),
        default=False,
        help_text='Whether the monthly goal of 3 calls has been completed'
    )
    goal_completed_at = models.DateTimeField(
        _('Goal Completed At'),
        null=True,
        blank=True,
        help_text='When the monthly goal was completed'
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Monthly Donation Tracker')
        verbose_name_plural = _('Monthly Donation Trackers')
        unique_together = ['user', 'month']
        ordering = ['-month']
        indexes = [
            models.Index(fields=['user', 'month']),
            models.Index(fields=['monthly_goal_completed']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.month.strftime('%B %Y')} ({self.completed_calls_count}/3)"

    def increment_call_count(self):
        """Increment the completed calls count and check if monthly goal is reached."""
        self.completed_calls_count += 1
        if self.completed_calls_count >= 3 and not self.monthly_goal_completed:
            self.monthly_goal_completed = True
            self.goal_completed_at = timezone.now()
        self.save()
        return self.monthly_goal_completed

    def reset_for_new_month(self):
        """Reset the tracker for a new month."""
        # Store previous blocked status for email notification
        was_blocked = self.monthly_goal_completed and not self.user.is_active
        
        # Reset monthly tracking fields
        self.completed_calls_count = 0
        self.monthly_goal_completed = False
        self.goal_completed_at = None
        
        # Unblock the user for the new month if they were blocked
        if not self.user.is_active:
            self.user.is_active = True
            self.user.save()
            
            # Send unblock notification email
            if was_blocked:
                self._send_unblock_email_notification()
        
        self.save()
        return self
    
    @classmethod
    def get_or_create_for_user_month(cls, user, date=None):
        """Get or create a tracker for the user's current month."""
        if date is None:
            date = timezone.now().date()
        
        # Get the first day of the month
        month_start = date.replace(day=1)
        
        # Check if user has a tracker for previous month that was completed
        # If so, and we're in a new month, reset the blocking status
        previous_trackers = cls.objects.filter(
            user=user,
            month__lt=month_start,
            monthly_goal_completed=True
        ).order_by('-month')
        
        # If there's a previous completed tracker and we're in a new month,
        # the user should be unblocked for the new month
        tracker, created = cls.objects.get_or_create(
            user=user,
            month=month_start,
            defaults={
                'completed_calls_count': 0,
                'monthly_goal_completed': False,
                'goal_completed_at': None
            }
        )
        
        # If tracker already exists but we're checking in a new month,
        # ensure it's properly reset (this handles edge cases)
        if not created and tracker.month == month_start:
            current_month = timezone.now().date().replace(day=1)
            if tracker.month < current_month:
                tracker.reset_for_new_month()
        
        return tracker, created


# Signal to automatically handle monthly resets
@receiver(post_save, sender=MonthlyDonationTracker)
def handle_monthly_reset(sender, instance, created, **kwargs):
    """
    Signal to automatically reset monthly counts when a new month begins.
    This ensures users are unblocked at the start of each new month.
    """
    if created:
        # When a new tracker is created, check if user was blocked in previous month
        current_month = instance.month
        previous_month = (current_month.replace(day=1) - datetime.timedelta(days=1)).replace(day=1)
        
        try:
            # Check if user was blocked in previous month
            prev_tracker = MonthlyDonationTracker.objects.get(
                user=instance.user,
                month=previous_month,
                monthly_goal_completed=True,
                completed_calls_count__gte=3
            )
            
            # If user was blocked, ensure current tracker is reset
            if instance.monthly_goal_completed or instance.completed_calls_count > 0:
                instance.reset_for_new_month()
                
                # Send email notification about unblocking
                month_year = current_month.strftime('%B %Y')
                _send_unblock_email_notification(instance.user, month_year)
                
                # Log the automatic reset
                print(f"Auto-reset: User {instance.user.email} unblocked for {month_year}")
                
        except MonthlyDonationTracker.DoesNotExist:
            # No previous month tracker found, nothing to reset
            pass
        except Exception as e:
            # Log any errors but don't break the flow
            print(f"Error in monthly reset signal for {instance.user.email}: {e}")


def _send_unblock_email_notification(user, month_year):
    """
    Send email notification to user when they get unblocked.
    
    Args:
        user: User object
        month_year (str): Month and year (e.g., "January 2025")
    """
    try:
        from .email_config import EmailService
        
        success, message = EmailService.send_monthly_unblock_notification(user, month_year)
        
        if success:
            print(f"Unblock email sent to {user.email} for {month_year}")
        else:
            print(f"Failed to send unblock email to {user.email}: {message}")
            
    except ImportError:
        print(f"EmailService not available - could not send unblock email to {user.email}")
    except Exception as e:
        print(f"Error sending unblock email to {user.email}: {e}")