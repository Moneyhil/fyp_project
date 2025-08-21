from django.core.management.base import BaseCommand
from donation.models import User, Profile
from donation.email_config import EmailService
from django.utils import timezone
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Test admin actions for block/unblock and delete functionality'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--create-test-users',
            action='store_true',
            help='Create test users for testing admin actions',
        )
        parser.add_argument(
            '--test-email',
            type=str,
            help='Test email functionality with specified email address',
        )
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Clean up test users created by this command',
        )
    
    def handle(self, *args, **options):
        if options['create_test_users']:
            self.create_test_users()
        elif options['test_email']:
            self.test_email_functionality(options['test_email'])
        elif options['cleanup']:
            self.cleanup_test_users()
        else:
            self.show_admin_actions_info()
    
    def create_test_users(self):
        """Create test users for admin actions testing"""
        self.stdout.write('Creating test users for admin actions testing...')
        self.stdout.write('-' * 60)
        
        test_users = [
            {
                'email': 'testuser1@example.com',
                'name': 'Test User One',
                'is_active': True
            },
            {
                'email': 'testuser2@example.com', 
                'name': 'Test User Two',
                'is_active': False  # Already blocked
            },
            {
                'email': 'testuser3@example.com',
                'name': 'Test User Three', 
                'is_active': True
            }
        ]
        
        created_count = 0
        for user_data in test_users:
            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    'name': user_data['name'],
                    'is_active': user_data['is_active'],
                    'is_verified': True
                }
            )
            
            if created:
                # Create profile for the user
                Profile.objects.get_or_create(
                    user=user,
                    defaults={
                        'first_name': user_data['name'].split()[0],
                        'last_name': user_data['name'].split()[-1],
                        'contact_number': f'12345678{user.id:03d}',  # Ensure 11 digits
                        'city': 'Test City',
                        'blood_group': 'O+',
                        'role': 'donor'
                    }
                )
                created_count += 1
                status = 'BLOCKED' if not user_data['is_active'] else 'ACTIVE'
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {user_data["email"]} - Status: {status}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Already exists: {user_data["email"]}')
                )
        
        self.stdout.write('-' * 60)
        self.stdout.write(f'Created {created_count} new test users')
        self.stdout.write('\n📋 ADMIN ACTIONS TESTING GUIDE:')
        self.stdout.write('=' * 60)
        self.stdout.write('1. Go to Django Admin: /admin/')
        self.stdout.write('2. Navigate to Users, Profiles, or Blocked Profiles')
        self.stdout.write('3. Select test users and try these actions:')
        self.stdout.write('   • Block selected user accounts')
        self.stdout.write('   • Unblock selected user accounts')
        self.stdout.write('   • Delete selected user profiles')
        self.stdout.write('4. Check email notifications for unblock actions')
        self.stdout.write('5. Verify status changes in the admin interface')
        self.stdout.write('=' * 60)
    
    def test_email_functionality(self, email):
        """Test email functionality for admin actions"""
        self.stdout.write(f'Testing email functionality for: {email}')
        self.stdout.write('-' * 60)
        
        # Create a mock user for testing
        class MockUser:
            def __init__(self, email, name):
                self.email = email
                self.name = name
        
        user = MockUser(email, email.split('@')[0].title())
        current_month = timezone.now().strftime('%B %Y')
        
        try:
            success, message = EmailService.send_monthly_unblock_notification(user, current_month)
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS('✓ Email notification sent successfully!')
                )
                self.stdout.write(f'Message: {message}')
            else:
                self.stdout.write(
                    self.style.ERROR('✗ Failed to send email notification')
                )
                self.stdout.write(f'Error: {message}')
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Exception occurred: {e}')
            )
        
        self.stdout.write('-' * 60)
        self.stdout.write('Email test completed!')
    
    def cleanup_test_users(self):
        """Clean up test users created by this command"""
        self.stdout.write('Cleaning up test users...')
        self.stdout.write('-' * 60)
        
        test_emails = [
            'testuser1@example.com',
            'testuser2@example.com', 
            'testuser3@example.com'
        ]
        
        deleted_count = 0
        for email in test_emails:
            try:
                user = User.objects.get(email=email)
                user.delete()
                deleted_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Deleted: {email}')
                )
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Not found: {email}')
                )
        
        self.stdout.write('-' * 60)
        self.stdout.write(f'Deleted {deleted_count} test users')
    
    def show_admin_actions_info(self):
        """Show information about available admin actions"""
        self.stdout.write('🔧 ADMIN ACTIONS OVERVIEW')
        self.stdout.write('=' * 60)
        
        self.stdout.write('\n📊 AVAILABLE ADMIN INTERFACES:')
        self.stdout.write('1. Users (/admin/donation/user/)')
        self.stdout.write('   • Block/Unblock user accounts (non-staff only)')
        self.stdout.write('   • Delete user accounts (non-staff only)')
        self.stdout.write('   • View user status (Staff/Active/Blocked)')
        
        self.stdout.write('\n2. Profiles (/admin/donation/profile/)')
        self.stdout.write('   • Block/Unblock user accounts')
        self.stdout.write('   • Delete user profiles and accounts')
        self.stdout.write('   • View account status (Active/Blocked)')
        
        self.stdout.write('\n3. Blocked Profiles (/admin/donation/blockedprofiles/)')
        self.stdout.write('   • Reset monthly count for current month')
        self.stdout.write('   • Block/Unblock user accounts')
        self.stdout.write('   • Delete user profiles')
        self.stdout.write('   • View monthly tracking status')
        
        self.stdout.write('\n📧 EMAIL NOTIFICATIONS:')
        self.stdout.write('• Automatic email sent when users are unblocked')
        self.stdout.write('• Professional template with account status info')
        self.stdout.write('• Error handling for failed email delivery')
        
        self.stdout.write('\n🛡️ SAFETY FEATURES:')
        self.stdout.write('• Staff accounts protected from deletion')
        self.stdout.write('• Comprehensive error handling')
        self.stdout.write('• Success/failure feedback messages')
        self.stdout.write('• Email delivery confirmation')
        
        self.stdout.write('\n🧪 TESTING COMMANDS:')
        self.stdout.write('• Create test users: --create-test-users')
        self.stdout.write('• Test email: --test-email user@example.com')
        self.stdout.write('• Cleanup: --cleanup')
        
        self.stdout.write('\n📈 CURRENT STATISTICS:')
        total_users = User.objects.filter(is_staff=False).count()
        active_users = User.objects.filter(is_staff=False, is_active=True).count()
        blocked_users = User.objects.filter(is_staff=False, is_active=False).count()
        
        self.stdout.write(f'• Total Users: {total_users}')
        self.stdout.write(f'• Active Users: {active_users}')
        self.stdout.write(f'• Blocked Users: {blocked_users}')
        
        self.stdout.write('=' * 60)
        self.stdout.write('Use --help to see all available options')