import logging
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
logger = logging.getLogger(__name__)

class DonationRequestService:
    
    @staticmethod
    def create_donation_request(requester, donor, blood_group, notes=''):
 
        from .models import DonationRequest
        
        try:
            donation_request = DonationRequest.objects.create(
                requester=requester,
                donor=donor,
                blood_group=blood_group,
                notes=notes
            )
            
            # Donation request created successfully
            logger.info(f"Donation request {donation_request.id} created successfully")
            
            return donation_request
            
        except Exception as e:
            logger.error(f"Failed to create donation request: {str(e)}")
            raise
    
    @staticmethod
    def create_donation_request_with_notification(requester, donor, blood_group, notes=''):
        """
        Create a donation request and send notification to donor.
        """
        from .models import DonationRequest
        from .email_config import EmailService
        
        try:
            donation_request = DonationRequest.objects.create(
                requester=requester,
                donor=donor,
                blood_group=blood_group,
                notes=notes
            )
            
            # Send notification 
            try:
                success, message = EmailService.send_donation_reminder_email(donor, donation_request)
                if success:
                    logger.info(f"Notification email sent to donor {donor.email} for donation request {donation_request.id}")
                else:
                    logger.warning(f"Failed to send notification email to donor {donor.email}: {message}")
            except Exception as email_error:
                logger.error(f"Error sending notification email: {str(email_error)}")
                # Don't fail the entire request if email fails
            
            return donation_request
            
        except Exception as e:
            logger.error(f"Failed to create donation request with notification: {str(e)}")
            raise
    
    @staticmethod
    def send_response_notification(donation_request,response, notes):
    
        from .email_config import EmailService
        
        try:
            # boolean response
            response_type = 'accepted' if response else 'declined'
            
            if response_type == 'accepted':
                subject = 'Donation Request Accepted'
                message = f'''
                Dear {donation_request.requester.name},
                
                Good news! {donation_request.donor.name} has accepted your blood donation request.
                
                Request Details:
                - Blood Type: {donation_request.blood_group}
                - Notes: {donation_request.notes}
                - Response Notes: {notes}
                
                Please coordinate with the donor for the donation process.
                
                Best regards,
                Blood Donation Team
                '''
            else:
                subject = 'Donation Request Declined'
                message = f'''
                Dear {donation_request.requester.name},
                
                We regret to inform you that {donation_request.donor.name} has declined your blood donation request.
                
                Request Details:
                - Blood Type: {donation_request.blood_group}
                - Response Notes: {notes}
                
                Please consider reaching out to other potential donors.
                
                Best regards,
                Blood Donation Team
                '''
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[donation_request.requester.email],
                fail_silently=False,
            )
            
            logger.info(f"Response notification sent to requester {donation_request.requester.email}")
            return True, "Response notification sent successfully"
            
        except Exception as e:
            logger.error(f"Failed to send response notification: {str(e)}")
            return False, str(e)
