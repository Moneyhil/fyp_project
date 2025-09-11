from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """
    Service class for handling email operations
    """
    
    @staticmethod
    def send_monthly_unblock_notification(user, month_year):
        """
        Send email notification when user gets unblocked for monthly donations
        """
        try:
            subject = f'Account Unblocked - {month_year}'
            message = f'''
            Dear {user.name},
            
            Your account has been unblocked for {month_year}.
            You can now participate in blood donation activities.
            
            Thank you for your continued support!
            
            Best regards,
            Blood Donation Team
            '''
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            
            return True, "Email sent successfully"
            
        except Exception as e:
            logger.error(f"Failed to send unblock notification email to {user.email}: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def send_donor_confirmation_email(donor_user, caller_user, call_log_id):
        """
        Send email to donor asking for blood donation confirmation with clickable links
        """
        try:
            subject = 'Blood Donation Confirmation Required'
            
            # Use BASE_URL from settings for backend confirmation links
            base_url = getattr(settings, 'BASE_URL', 'http://192.168.100.16:8000')
            yes_url = f"{base_url}/donation/confirm-donation/?call_log_id={call_log_id}&response=yes"
            no_url = f"{base_url}/donation/confirm-donation/?call_log_id={call_log_id}&response=no"
            
            message = f"""
            Dear {donor_user.name},
            
            {caller_user.name} has requested your participation in a blood donation drive.
            
            Please confirm your availability by clicking one of the links below:
            
             YES - I can donate: {yes_url}
            
             NO - I cannot donate: {no_url}
            
            Thank you for your time and consideration.
            
            Best regards,
            Blood Donation Team
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[donor_user.email],
                fail_silently=False,
            )
            
            return True, "Confirmation email sent successfully"
            
        except Exception as e:
            logger.error(f"Failed to send confirmation email to {donor_user.email}: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def send_donation_reminder_email(user, donation_request):
        """
        Send reminder email for pending donation requests
        """
        try:
            subject = 'Blood Donation Reminder'
            message = f'''
            Dear {user.name},
            
            This is a reminder about your pending blood donation request.
            
            Request Details:
            - Blood Type: {donation_request.blood_group}
            - Requester: {donation_request.requester.name}
            - Notes: {donation_request.notes or 'No additional notes'}
            
            Please consider donating blood to help save lives.
            
            Thank you for your support!
            
            Best regards,
            Blood Donation Team
            '''
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            
            return True, "Reminder email sent successfully"
            
        except Exception as e:
            logger.error(f"Failed to send reminder email to {user.email}: {str(e)}")
            return False, str(e)