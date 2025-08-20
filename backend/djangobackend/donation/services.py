import logging
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from .models import Message
from .email_config import EmailService

logger = logging.getLogger(__name__)

class NotificationService:
    """
    Service class for handling various types of notifications including SMS and email.
    """
    
    @staticmethod
    def send_sms(phone_number, message_content):
        """
        Send SMS notification to the given phone number.
        Currently disabled - using email notifications instead.
        """
        try:
            # SMS functionality disabled - using email as primary notification method
            logger.info(f"SMS notification logged (not sent) to {phone_number}: {message_content}")
            return True
        except Exception as e:
            logger.error(f"Failed to log SMS for {phone_number}: {str(e)}")
            return False
    
    @staticmethod
    def send_email_notification(email, subject, message_content):
        """
        Send email notification as a fallback or additional notification method.
        """
        try:
            send_mail(
                subject=subject,
                message=message_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {email}: {str(e)}")
            return False
    
    @staticmethod
    def process_message_notifications(message_id):
        """
        Process and send notifications for a given message.
        """
        try:
            message = Message.objects.get(id=message_id)
            
            # Send email notification as primary method
            recipient_email = None
            if hasattr(message.recipient, 'email') and message.recipient.email:
                recipient_email = message.recipient.email
            elif hasattr(message.recipient, 'profile') and hasattr(message.recipient.profile, 'email'):
                recipient_email = message.recipient.profile.email
            
            if recipient_email:
                email_content = f"{message.content}\n\nPhone: {message.phone_number or 'Not provided'}"
                email_sent = NotificationService.send_email_notification(
                    recipient_email,
                    message.subject,
                    email_content
                )
                
                if email_sent:
                    message.email_sent = True
                    message.email_sent_at = timezone.now()
                    message.save()
            
            # Log SMS attempt (not actually sent)
            if message.is_sms and message.phone_number:
                sms_content = f"{message.subject}\n\n{message.content}"
                sms_logged = NotificationService.send_sms(message.phone_number, sms_content)
                
                if sms_logged:
                    message.sms_sent = True
                    message.sms_sent_at = timezone.now()
                    message.save()
            
            return True
            
        except Message.DoesNotExist:
            logger.error(f"Message with id {message_id} not found")
            return False
        except Exception as e:
            logger.error(f"Failed to process notifications for message {message_id}: {str(e)}")
            return False

class DonationRequestService:
    """
    Service class for handling donation request business logic.
    """
    
    @staticmethod
    def create_donation_request_with_notification(requester, donor, blood_group, urgency_level='medium', notes=''):
        """
        Create a donation request and send initial notification to donor.
        """
        from .models import DonationRequest, Message
        
        try:
            # Create donation request
            donation_request = DonationRequest.objects.create(
                requester=requester,
                donor=donor,
                blood_group=blood_group,
                urgency_level=urgency_level,
                notes=notes
            )
            
            # Create notification message
            message_content = (
                f"Hello {donor.name},\n\n"
                f"You have received a blood donation request from {requester.name} "
                f"for {blood_group} blood group.\n\n"
                f"Urgency Level: {urgency_level.upper()}\n"
            )
            
            if notes:
                message_content += f"Additional Notes: {notes}\n\n"
            
            message_content += (
                "Please open the Blood Donation app to respond to this request.\n\n"
                "Thank you for being a potential life saver!"
            )
            
            message = Message.objects.create(
                donation_request=donation_request,
                sender=requester,
                recipient=donor,
                message_type='alert',
                subject='Blood Donation Request',
                content=message_content,
                phone_number=getattr(donor.profile, 'contact_number', None) if hasattr(donor, 'profile') else None,
                is_sms=True
            )
            
            # Process notifications asynchronously (in production, use Celery)
            NotificationService.process_message_notifications(message.id)
            
            return donation_request
            
        except Exception as e:
            logger.error(f"Failed to create donation request with notification: {str(e)}")
            raise
    
    @staticmethod
    def send_response_notification(donation_request, responder, response, notes=''):
        """
        Send notification when someone responds to a donation request.
        """
        from .models import Message
        
        try:
            # Determine the recipient (the other party)
            if responder == donation_request.requester:
                recipient = donation_request.donor
                responder_role = 'requester'
            else:
                recipient = donation_request.requester
                responder_role = 'donor'
            
            # Create response message
            action = "accepted" if response else "declined"
            
            if responder_role == 'donor':
                if response:
                    message_content = (
                        f"Great news! {responder.name} has agreed to donate {donation_request.blood_group} blood to you.\n\n"
                        "Please coordinate with the donor for the donation process.\n\n"
                    )
                else:
                    message_content = (
                        f"{responder.name} is unable to donate blood at this time.\n\n"
                        "Please try contacting other donors or search for more donors in your area.\n\n"
                    )
            else:
                if response:
                    message_content = (
                        f"{responder.name} has confirmed they still need {donation_request.blood_group} blood donation.\n\n"
                        "Please proceed with your donation if you're still available.\n\n"
                    )
                else:
                    message_content = (
                        f"{responder.name} no longer needs blood donation.\n\n"
                        "Thank you for your willingness to help!\n\n"
                    )
            
            if notes:
                message_content += f"Additional message: {notes}\n\n"
            
            message_content += "Thank you for using our Blood Donation app!"
            
            message = Message.objects.create(
                donation_request=donation_request,
                sender=responder,
                recipient=recipient,
                message_type='confirmation',
                subject=f'Donation Request {action.title()}',
                content=message_content,
                phone_number=getattr(recipient.profile, 'contact_number', None) if hasattr(recipient, 'profile') else None,
                is_sms=True
            )
            
            # Process notifications
            NotificationService.process_message_notifications(message.id)
            
            return message
            
        except Exception as e:
            logger.error(f"Failed to send response notification: {str(e)}")
            raise

class CallLogService:
    """
    Service class for handling call log operations.
    """
    
    @staticmethod
    def log_call_with_outcome(caller, recipient, donation_request=None, duration=0, outcome='completed', notes=''):
        """
        Log a call and send follow-up notifications if needed.
        """
        from .models import CallLog
        
        try:
            call_log = CallLog.objects.create(
                caller=caller,
                recipient=recipient,
                donation_request=donation_request,
                duration=duration,
                outcome=outcome,
                notes=notes
            )
            
            # If call was unsuccessful, might want to send a follow-up message
            if outcome in ['no_answer', 'busy', 'failed'] and donation_request:
                follow_up_message = (
                    f"We tried to reach you regarding a blood donation request but couldn't connect.\n\n"
                    f"Please check your messages in the Blood Donation app for important requests.\n\n"
                    "Your response could help save a life!"
                )
                
                from .models import Message
                Message.objects.create(
                    donation_request=donation_request,
                    sender=caller,
                    recipient=recipient,
                    message_type='reminder',
                    subject='Missed Call - Blood Donation Request',
                    content=follow_up_message,
                    phone_number=getattr(recipient.profile, 'contact_number', None) if hasattr(recipient, 'profile') else None,
                    is_sms=True
                )
            
            return call_log
            
        except Exception as e:
            logger.error(f"Failed to log call: {str(e)}")
            raise