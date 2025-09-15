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
        
        try:
            validate_email(email)
            return True
        except ValidationError:
            return False

    def create_user(self, email, name, password=None, **extra_fields):
        
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
    
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
            
        return self.create_user(email, name, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    
    name = models.CharField(_('Full Name'), max_length=150)
    email = models.EmailField(_('Email Address'), unique=True)
    
  
    otp_secret = models.CharField(max_length=128, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    otp_expires_at = models.DateTimeField(null=True, blank=True)
    
 
    is_verified = models.BooleanField(_('Verified'), default=False)
    is_active = models.BooleanField(_('Active'), default=True)
    is_staff = models.BooleanField(_('Staff status'), default=False)
    
 
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
        
        raw_otp = ''.join(secrets.choice('0123456789') for _ in range(6))
        self.otp_secret = hashlib.sha256(raw_otp.encode()).hexdigest()
        self.otp_created_at = timezone.now()
        self.otp_expires_at = self.otp_created_at + datetime.timedelta(minutes=expiry_minutes)
        self.save(update_fields=['otp_secret', 'otp_created_at', 'otp_expires_at'])
        return raw_otp

    def verify_otp(self, otp):

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
        
        self.otp_secret = None
        self.otp_created_at = None
        self.otp_expires_at = None


class Admin(models.Model):

    name = models.CharField(_('Full Name'), max_length=150)
    email = models.EmailField(_('Email Address'), unique=True)
    password = models.CharField(_('Password'), max_length=128)
    

    is_active = models.BooleanField(_('Active'), default=True)
    is_superuser = models.BooleanField(_('Superuser'), default=False)
    
   
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
        
        super().clean()
        if self.email:
            self.email = self.email.lower()
    
    def set_password(self, raw_password):
     
        from django.contrib.auth.hashers import make_password
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password)


class Profile(models.Model):
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
      
        from django.core.exceptions import ValidationError
        import re
        
        
        if self.contact_number:
            
            clean_number = self.contact_number.replace(' ', '').replace('-', '')
            if not re.match(r'^[0-9]{11}$', clean_number):
                raise ValidationError({
                    'contact_number': 'Contact number must be exactly 11 numeric digits'
                })
        
    
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
        

        if self.city:
            if not re.match(r'^[a-zA-Z\s]+$', self.city):
                raise ValidationError({
                    'city': 'City name should only contain letters and spaces'
                })
    
    def save(self, *args, **kwargs):
      
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.email} - Profile"
    
    @property
    def full_name(self):
       
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or self.user.name


class DonationRequest(models.Model):
  
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
        related_name='donation_requests_made'
    )
    donor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='donation_requests_received'
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
        ]
    )
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    user_response = models.BooleanField(
        _('User Response'),
        null=True,
        blank=True
    )
    donor_response = models.BooleanField(
        _('Donor Response'),
        null=True,
        blank=True
    )

    notes = models.TextField(
        _('Notes'),
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    expires_at = models.DateTimeField(
        _('Expires At'),
        null=True,
        blank=True
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
    call_method = models.CharField(
        _('Call Method'),
        max_length=10,
        choices=[
            ('dialer', 'Phone Dialer'),
            ('whatsapp', 'WhatsApp Call'),
        ],
        default='dialer',
        help_text='Method used to make the call'
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
  
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='monthly_trackers'
    )
    month = models.DateField(
        _('Month')
    )
    completed_calls_count = models.PositiveIntegerField(
        _('Completed Calls Count'),
        default=0
    )
    monthly_goal_completed = models.BooleanField(
        _('Monthly Goal Completed'),
        default=False
    )
    goal_completed_at = models.DateTimeField(
        _('Goal Completed At'),
        null=True,
        blank=True
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
        
        self.completed_calls_count += 1
        if self.completed_calls_count >= 3 and not self.monthly_goal_completed:
            self.monthly_goal_completed = True
            self.goal_completed_at = timezone.now()
        self.save()
        return self.monthly_goal_completed

    def reset_for_new_month(self):
        
        was_blocked = self.monthly_goal_completed and not self.user.is_active
        
        
        self.completed_calls_count = 0
        self.monthly_goal_completed = False
        self.goal_completed_at = None
       
        if not self.user.is_active:
            self.user.is_active = True
            self.user.save()
            
      
            if was_blocked:
                self._send_unblock_email_notification()
        
        self.save()
        return self
    
    @classmethod
    def get_or_create_for_user_month(cls, user, date=None):
    
        if date is None:
            date = timezone.now().date()
        
        month_start = date.replace(day=1)
        
        previous_trackers = cls.objects.filter(
            user=user,
            month__lt=month_start,
            monthly_goal_completed=True
        ).order_by('-month')
        
    
        tracker, created = cls.objects.get_or_create(
            user=user,
            month=month_start,
            defaults={
                'completed_calls_count': 0,
                'monthly_goal_completed': False,
                'goal_completed_at': None
            }
        )
        
        if not created and tracker.month == month_start:
            current_month = timezone.now().date().replace(day=1)
            if tracker.month < current_month:
                tracker.reset_for_new_month()
        
        return tracker, created



@receiver(post_save, sender=MonthlyDonationTracker)
def handle_monthly_reset(sender, instance, created, **kwargs):

    if created:
       
        current_month = instance.month
        previous_month = (current_month.replace(day=1) - datetime.timedelta(days=1)).replace(day=1)
        
        try:
            prev_tracker = MonthlyDonationTracker.objects.get(
                user=instance.user,
                month=previous_month,
                monthly_goal_completed=True,
                completed_calls_count__gte=3
            )
            
            if instance.monthly_goal_completed or instance.completed_calls_count > 0:
                instance.reset_for_new_month()
                
                
                month_year = current_month.strftime('%B %Y')
                _send_unblock_email_notification(instance.user, month_year)
                print(f"Auto-reset: User {instance.user.email} unblocked for {month_year}")
                
        except MonthlyDonationTracker.DoesNotExist:
            
            pass
        except Exception as e:
            
            print(f"Error in monthly reset signal for {instance.user.email}: {e}")


def _send_unblock_email_notification(user, month_year):
 
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


manual_block_override = models.BooleanField(default=False, help_text="Prevents automatic re-blocking")