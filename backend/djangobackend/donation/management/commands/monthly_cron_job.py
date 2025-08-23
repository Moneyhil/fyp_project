from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils import timezone
from django.conf import settings
import logging
import os
import traceback


class Command(BaseCommand):
    help = 'Wrapper command for monthly reset cron job with enhanced logging'
    
    def handle(self, *args, **options):
        # Setup logging
        log_file = os.path.join(settings.BASE_DIR, 'logs', 'monthly_cron.log')
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        logger = logging.getLogger(__name__)
        
        try:
            start_time = timezone.now()
            logger.info(f'Starting monthly reset cron job at {start_time}')
            
            # Call the actual reset command
            call_command('reset_monthly_counts')
            
            end_time = timezone.now()
            duration = end_time - start_time
            logger.info(f'Monthly reset completed successfully in {duration.total_seconds():.2f} seconds')
            
            self.stdout.write(
                self.style.SUCCESS(f'Monthly reset cron job completed successfully at {end_time}')
            )
            
        except Exception as e:
            error_time = timezone.now()
            error_msg = f'Monthly reset cron job failed at {error_time}: {str(e)}'
            logger.error(error_msg)
            logger.error(f'Traceback: {traceback.format_exc()}')
            
            self.stdout.write(
                self.style.ERROR(error_msg)
            )
            
            # Re-raise the exception so cron knows it failed
            raise e