from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:
    
    @staticmethod
    def send_monthly_unblock_notification(user, month_year):
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
        try:
            logger.info(f"Attempting to send confirmation email to {donor_user.email}")
            
            subject = 'Blood Donation Confirmation Required'
            base_url = getattr(settings, 'BASE_URL', 'http://192.168.100.16:8000')
            yes_url = f"{base_url}/donation/confirm-donation/?call_log_id={call_log_id}&response=yes"
            no_url = f"{base_url}/donation/confirm-donation/?call_log_id={call_log_id}&response=no"
            
            logger.info(f"Email URLs - Yes: {yes_url}, No: {no_url}")
            
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
            
            logger.info(f"Email sent successfully to {donor_user.email}")
            return True, "Confirmation email sent successfully"
            
        except Exception as e:
            logger.error(f"Failed to send confirmation email to {donor_user.email}: {str(e)}")
            return False, str(e)
    
   
  