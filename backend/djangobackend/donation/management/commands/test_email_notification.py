from django.core.management.base import BaseCommand
from donation.models import User
from donation.email_config import EmailService
from django.utils import timezone


class Command(BaseCommand):
    help = 'Test email notification functionality for monthly unblock notifications'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email address to send test notification to',
            required=True
        )
        parser.add_argument(
            '--month',
            type=str,
            help='Month and year for the notification (e.g., "January 2025")',
            default=timezone.now().strftime('%B %Y')
        )
    
    def handle(self, *args, **options):
        email = options['email']
        month_year = options['month']
        
        self.stdout.write(f'Testing email notification functionality...')
        self.stdout.write(f'Recipient: {email}')
        self.stdout.write(f'Month: {month_year}')
        self.stdout.write('-' * 50)
        
        # Try to find user by email, or create a mock user object
        try:
            user = User.objects.get(email=email)
            self.stdout.write(f'Found user: {user.name} ({user.email})')
        except User.DoesNotExist:
            # Create a mock user object for testing
            class MockUser:
                def __init__(self, email):
                    self.email = email
                    self.name = email.split('@')[0].title()
            
            user = MockUser(email)
            self.stdout.write(f'Using mock user: {user.name} ({user.email})')
        
        # Test the email notification
        try:
            success, message = EmailService.send_monthly_unblock_notification(user, month_year)
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Email notification sent successfully!')
                )
                self.stdout.write(f'Message: {message}')
            else:
                self.stdout.write(
                    self.style.ERROR(f'✗ Failed to send email notification')
                )
                self.stdout.write(f'Error: {message}')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Exception occurred while sending email: {e}')
            )
        
        self.stdout.write('-' * 50)
        self.stdout.write('Test completed!')
        
        # Show email template preview
        self.stdout.write('\n📧 EMAIL TEMPLATE PREVIEW:')
        self.stdout.write('=' * 60)
        
        from donation.email_config import get_email_template
        
        subject, message_content = get_email_template(
            'monthly_unblock',
            user_name=user.name,
            month_year=month_year
        )
        
        if subject and message_content:
            self.stdout.write(f'Subject: {subject}')
            self.stdout.write('\nMessage:')
            self.stdout.write(message_content)
        else:
            self.stdout.write(self.style.ERROR('Failed to get email template'))
        
        self.stdout.write('=' * 60)