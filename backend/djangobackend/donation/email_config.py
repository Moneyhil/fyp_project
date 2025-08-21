# Email Configuration for Blood Donation App
# This file contains configuration settings for email integration
# SMS functionality has been disabled in favor of email notifications

from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# SMS Service Configuration
SMS_CONFIG = {
    'ENABLED': getattr(settings, 'SMS_ENABLED', False),
    'PROVIDER': getattr(settings, 'SMS_PROVIDER', 'twilio'),  # Options: 'twilio', 'aws_sns', 'local'
    'RATE_LIMIT': getattr(settings, 'SMS_RATE_LIMIT', 10),  # Messages per minute
    'MAX_LENGTH': getattr(settings, 'SMS_MAX_LENGTH', 160),
}

# Twilio Configuration (Production)
TWILIO_CONFIG = {
    'ACCOUNT_SID': getattr(settings, 'TWILIO_ACCOUNT_SID', ''),
    'AUTH_TOKEN': getattr(settings, 'TWILIO_AUTH_TOKEN', ''),
    'PHONE_NUMBER': getattr(settings, 'TWILIO_PHONE_NUMBER', ''),
}

# AWS SNS Configuration (Alternative)
AWS_SNS_CONFIG = {
    'ACCESS_KEY_ID': getattr(settings, 'AWS_ACCESS_KEY_ID', ''),
    'SECRET_ACCESS_KEY': getattr(settings, 'AWS_SECRET_ACCESS_KEY', ''),
    'REGION': getattr(settings, 'AWS_SNS_REGION', 'us-east-1'),
}

# Message Templates
SMS_TEMPLATES = {
    'donation_request': (
        "Blood Donation Request: {requester_name} needs {blood_group} blood. "
        "Urgency: {urgency}. Open the app to respond. Thank you for saving lives!"
    ),
    'request_accepted': (
        "Great news! {donor_name} agreed to donate {blood_group} blood. "
        "Please coordinate the donation process. Thank you!"
    ),
    'request_declined': (
        "{donor_name} is unable to donate at this time. "
        "Please try contacting other donors. Thank you for understanding."
    ),
    'call_missed': (
        "Missed call regarding blood donation request. "
        "Please check the app for important messages. Your response could save a life!"
    ),
    'reminder': (
        "Reminder: You have pending blood donation requests. "
        "Please open the app to respond. Thank you!"
    )
}

# Email Templates
EMAIL_TEMPLATES = {
    'monthly_unblock': {
        'subject': 'Account Unblocked - Welcome Back to Blood Donation App',
        'message': '''
Dear {user_name},

Great news! Your account has been automatically unblocked for {month_year}.

Your previous monthly donation goal was completed in the last month, and now you can continue helping save lives with a fresh start.

📊 Monthly Status Reset:
• Completed calls count: Reset to 0
• Monthly goal status: Reset
• Account status: Active

You can now:
✓ Receive new donation requests
✓ Make calls to donors/requesters
✓ Continue your life-saving contributions

Thank you for being a valuable member of our blood donation community. Your dedication to helping others is truly appreciated.

Best regards,
Blood Donation App Team

Note: This is an automated message. If you have any questions, please contact our support team.
'''
    },
    'donation_request': {
        'subject': 'Blood Donation Request - {blood_group} Needed',
        'message': '''
Dear {recipient_name},

You have received a new blood donation request:

🩸 Blood Group Needed: {blood_group}
👤 Requester: {requester_name}
⚡ Urgency Level: {urgency}
📍 Location: {location}

Please open the Blood Donation App to respond to this request.

Your quick response could save a life!

Best regards,
Blood Donation App Team
'''
    },
    'call_confirmation': {
        'subject': 'Call Completed - Thank You for Your Contribution',
        'message': '''
Dear {user_name},

Thank you for completing a donation-related call!

📞 Call Details:
• Date: {call_date}
• Duration: {duration}
• Related to: {blood_group} donation request

📊 Your Monthly Progress:
• Completed calls this month: {completed_calls}/3
• Status: {status}

{additional_message}

Thank you for your continued support in saving lives!

Best regards,
Blood Donation App Team
'''
    }
}

def get_sms_template(template_name, **kwargs):
    """
    Get formatted SMS template with provided parameters.
    """
    template = SMS_TEMPLATES.get(template_name, '')
    try:
        return template.format(**kwargs)
    except KeyError as e:
        logger.error(f"Missing parameter {e} for SMS template {template_name}")
        return template

def validate_phone_number(phone_number):
    """
    Validate phone number format.
    """
    import re
    
    if not phone_number:
        return False
    
    # Remove all non-digit characters
    cleaned = re.sub(r'\D', '', phone_number)
    
    # Check if it's a valid length (10-15 digits)
    if len(cleaned) < 10 or len(cleaned) > 15:
        return False
    
    return True

def format_phone_number(phone_number):
    """
    Format phone number for SMS sending.
    """
    import re
    
    if not phone_number:
        return None
    
    # Remove all non-digit characters
    cleaned = re.sub(r'\D', '', phone_number)
    
    # Add country code if not present (assuming Pakistan +92)
    if len(cleaned) == 10:
        cleaned = '92' + cleaned
    elif len(cleaned) == 11 and cleaned.startswith('0'):
        cleaned = '92' + cleaned[1:]
    
    return '+' + cleaned

# Production SMS Integration Examples

def send_sms_twilio(phone_number, message):
    """
    Send SMS using Twilio (Production implementation).
    Note: Requires 'pip install twilio' and proper configuration.
    """
    try:
        # Uncomment and configure when twilio is installed
        # from twilio.rest import Client
        # 
        # client = Client(
        #     TWILIO_CONFIG['ACCOUNT_SID'],
        #     TWILIO_CONFIG['AUTH_TOKEN']
        # )
        # 
        # message = client.messages.create(
        #     body=message,
        #     from_=TWILIO_CONFIG['PHONE_NUMBER'],
        #     to=format_phone_number(phone_number)
        # )
        # 
        # logger.info(f"SMS sent successfully via Twilio: {message.sid}")
        # return True, message.sid
        
        logger.info(f"Twilio SMS would be sent to {phone_number}: {message}")
        return True, "mock_message_id"
        
    except Exception as e:
        logger.error(f"Failed to send SMS via Twilio: {str(e)}")
        return False, str(e)

def send_sms_aws_sns(phone_number, message):
    """
    Send SMS using AWS SNS (Production implementation).
    Note: Requires 'pip install boto3' and proper AWS configuration.
    """
    try:
        # Uncomment and configure when boto3 is installed
        # import boto3
        # 
        # sns = boto3.client(
        #     'sns',
        #     aws_access_key_id=AWS_SNS_CONFIG['ACCESS_KEY_ID'],
        #     aws_secret_access_key=AWS_SNS_CONFIG['SECRET_ACCESS_KEY'],
        #     region_name=AWS_SNS_CONFIG['REGION']
        # )
        # 
        # response = sns.publish(
        #     PhoneNumber=format_phone_number(phone_number),
        #     Message=message
        # )
        # 
        # logger.info(f"SMS sent successfully via AWS SNS: {response['MessageId']}")
        # return True, response['MessageId']
        
        logger.info(f"AWS SNS SMS would be sent to {phone_number}: {message}")
        return True, "mock_message_id"
        
    except Exception as e:
        logger.error(f"Failed to send SMS via AWS SNS: {str(e)}")
        return False, str(e)

# Settings to add to Django settings.py for production:
"""
# SMS Configuration
SMS_ENABLED = True
SMS_PROVIDER = 'twilio'  # or 'aws_sns'
SMS_RATE_LIMIT = 10
SMS_MAX_LENGTH = 160

# Twilio Settings (if using Twilio)
TWILIO_ACCOUNT_SID = 'your_twilio_account_sid'
TWILIO_AUTH_TOKEN = 'your_twilio_auth_token'
TWILIO_PHONE_NUMBER = 'your_twilio_phone_number'

# AWS SNS Settings (if using AWS SNS)
AWS_ACCESS_KEY_ID = 'your_aws_access_key'
AWS_SECRET_ACCESS_KEY = 'your_aws_secret_key'
AWS_SNS_REGION = 'us-east-1'

# Email Settings (for fallback notifications)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email@gmail.com'
EMAIL_HOST_PASSWORD = 'your_app_password'
DEFAULT_FROM_EMAIL = 'Blood Donation App <your_email@gmail.com>'
"""

def get_email_template(template_name, **kwargs):
    """
    Get formatted email template with provided parameters.
    
    Args:
        template_name (str): Name of the template
        **kwargs: Template parameters
    
    Returns:
        tuple: (subject, message) or (None, None) if template not found
    """
    if template_name not in EMAIL_TEMPLATES:
        logger.error(f"Email template '{template_name}' not found")
        return None, None
    
    try:
        template = EMAIL_TEMPLATES[template_name]
        subject = template['subject'].format(**kwargs)
        message = template['message'].format(**kwargs)
        return subject, message
    except KeyError as e:
        logger.error(f"Missing parameter {e} for email template '{template_name}'")
        return None, None
    except Exception as e:
        logger.error(f"Error formatting email template '{template_name}': {str(e)}")
        return None, None


class EmailService:
    """
    Email service class for handling email notifications.
    This replaces the previous SMS functionality.
    """
    
    @staticmethod
    def send_email(email, subject, message):
        """
        Send email notification.
        
        Args:
            email (str): Recipient email address
            subject (str): Email subject
            message (str): Email message content
        
        Returns:
            tuple: (success, message)
        """
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            logger.info(f"Email sent successfully to {email}")
            return True, "Email sent successfully"
            
        except Exception as e:
            logger.error(f"Failed to send email to {email}: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def send_template_email(email, template_name, **kwargs):
        """
        Send email using a predefined template.
        
        Args:
            email (str): Recipient email address
            template_name (str): Name of the email template
            **kwargs: Template parameters
        
        Returns:
            tuple: (success, message)
        """
        subject, message = get_email_template(template_name, **kwargs)
        
        if subject is None or message is None:
            return False, f"Failed to get email template '{template_name}'"
        
        return EmailService.send_email(email, subject, message)
    
    @staticmethod
    def send_monthly_unblock_notification(user, month_year):
        """
        Send monthly unblock notification to user.
        
        Args:
            user: User object
            month_year (str): Month and year (e.g., "January 2025")
        
        Returns:
            tuple: (success, message)
        """
        try:
            user_name = getattr(user, 'name', user.email)
            
            return EmailService.send_template_email(
                email=user.email,
                template_name='monthly_unblock',
                user_name=user_name,
                month_year=month_year
            )
        except Exception as e:
            logger.error(f"Failed to send monthly unblock notification to {user.email}: {str(e)}")
            return False, str(e)