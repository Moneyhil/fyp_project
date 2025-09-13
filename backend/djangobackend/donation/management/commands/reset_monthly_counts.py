from django.core.management.base import BaseCommand
from django.utils import timezone
from donation.models import MonthlyDonationTracker
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Reset monthly donation counts for users when a new month begins'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--month',
            type=str,
            help='Specific month to reset in YYYY-MM format (default: current month)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be reset without actually doing it',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reset even if already done for the month',
        )
    
    def handle(self, *args, **options):
        
        if options['month']:
            try:
                target_date = datetime.strptime(options['month'], '%Y-%m').date()
                target_month = target_date.replace(day=1)
            except ValueError:
                self.stdout.write(
                    self.style.ERROR('Invalid month format. Use YYYY-MM (e.g., 2025-09)')
                )
                return
        else:
            target_month = timezone.now().date().replace(day=1)
        
        self.stdout.write(f'Processing monthly reset for: {target_month.strftime("%B %Y")}')
        
        # Find all users who were blocked in previous months
        previous_month = target_month - timedelta(days=1)
        previous_month_start = previous_month.replace(day=1)
        
        blocked_users_previous_month = MonthlyDonationTracker.objects.filter(
            month=previous_month_start,
            monthly_goal_completed=True,
            completed_calls_count__gte=3
        )
        
        self.stdout.write(f'Found {blocked_users_previous_month.count()} users blocked in previous month')
        
        reset_count = 0
        created_count = 0
        
        for prev_tracker in blocked_users_previous_month:
            user = prev_tracker.user
            
            # Get or create tracker for current month
            current_tracker, created = MonthlyDonationTracker.get_or_create_for_user_month(
                user=user,
                date=target_month
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    f'Created new tracker for {user.email} - {target_month.strftime("%B %Y")}'
                )
            else:
                # Check if this tracker needs to be reset
                if current_tracker.monthly_goal_completed and not options['force']:
                    self.stdout.write(
                        f'Skipping {user.email} - already completed goal this month'
                    )
                    continue
                
                if not options['dry_run']:
                    current_tracker.reset_for_new_month()
                    
                    # Send email notification
                    month_year = target_month.strftime('%B %Y')
                    self._send_unblock_email(user, month_year)
                    
                    reset_count += 1
                    self.stdout.write(
                        f'Reset tracker for {user.email} - {target_month.strftime("%B %Y")}'
                    )
                else:
                    reset_count += 1
                    self.stdout.write(
                        f'[DRY RUN] Would reset tracker for {user.email} - {target_month.strftime("%B %Y")}'
                    )
        
        
        current_month_trackers = MonthlyDonationTracker.objects.filter(
            month=target_month,
            monthly_goal_completed=True,
            completed_calls_count__gte=3
        )
        
        if current_month_trackers.exists() and options['force']:
            for tracker in current_month_trackers:
                if not options['dry_run']:
                    tracker.reset_for_new_month()
                    
                    # Send email notification
                    month_year = target_month.strftime('%B %Y')
                    self._send_unblock_email(tracker.user, month_year)
                    
                    reset_count += 1
                    self.stdout.write(
                        f'Force reset tracker for {tracker.user.email} - {target_month.strftime("%B %Y")}'
                    )
                else:
                    reset_count += 1
                    self.stdout.write(
                        f'[DRY RUN] Would force reset tracker for {tracker.user.email} - {target_month.strftime("%B %Y")}'
                    )
        

        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN COMPLETE: Would create {created_count} new trackers and reset {reset_count} existing trackers'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'RESET COMPLETE: Created {created_count} new trackers and reset {reset_count} existing trackers for {target_month.strftime("%B %Y")}'
                )
            )
        
        # Show current status
        current_blocked = MonthlyDonationTracker.objects.filter(
            month=target_month,
            monthly_goal_completed=True,
            completed_calls_count__gte=3
        ).count()
        
        self.stdout.write(
            f'Current blocked users for {target_month.strftime("%B %Y")}: {current_blocked}'
        )
    
    def _send_unblock_email(self, user, month_year):
        """
        Send email notification to user when they get unblocked.
        
        Args:
            user: User object
            month_year (str): Month and year (e.g., "January 2025")
        """
        try:
            from donation.email_config import EmailService
            
            success, message = EmailService.send_monthly_unblock_notification(user, month_year)
            
            if success:
                self.stdout.write(
                    f'  ✓ Unblock email sent to {user.email}'
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'  ⚠ Failed to send email to {user.email}: {message}')
                )
                
        except ImportError:
            self.stdout.write(
                self.style.WARNING(f'  ⚠ EmailService not available - could not send email to {user.email}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ✗ Error sending email to {user.email}: {e}')
            )