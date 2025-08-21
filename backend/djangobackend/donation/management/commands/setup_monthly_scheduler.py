from django.core.management.base import BaseCommand
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Setup instructions for scheduling monthly count resets'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Monthly Reset Scheduler Setup Instructions'))
        self.stdout.write('=' * 60)
        
        # Get the project path
        project_path = os.path.dirname(settings.BASE_DIR)
        manage_py_path = os.path.join(settings.BASE_DIR, 'manage.py')
        
        self.stdout.write('\n1. MANUAL RESET COMMANDS:')
        self.stdout.write('-' * 30)
        self.stdout.write('Reset for current month:')
        self.stdout.write(f'   python "{manage_py_path}" reset_monthly_counts')
        
        self.stdout.write('\nReset for specific month:')
        self.stdout.write(f'   python "{manage_py_path}" reset_monthly_counts --month 2025-02')
        
        self.stdout.write('\nDry run (preview what would be reset):')
        self.stdout.write(f'   python "{manage_py_path}" reset_monthly_counts --dry-run')
        
        self.stdout.write('\nForce reset (even if already done):')
        self.stdout.write(f'   python "{manage_py_path}" reset_monthly_counts --force')
        
        self.stdout.write('\n\n2. WINDOWS TASK SCHEDULER SETUP:')
        self.stdout.write('-' * 40)
        self.stdout.write('To automatically run monthly resets:')
        self.stdout.write('\na) Open Task Scheduler (taskschd.msc)')
        self.stdout.write('b) Create Basic Task...')
        self.stdout.write('c) Name: "Django Monthly Reset"')
        self.stdout.write('d) Trigger: Monthly, on the 1st day')
        self.stdout.write('e) Action: Start a program')
        self.stdout.write(f'f) Program: python')
        self.stdout.write(f'g) Arguments: "{manage_py_path}" reset_monthly_counts')
        self.stdout.write(f'h) Start in: "{settings.BASE_DIR}"')
        
        self.stdout.write('\n\n3. ALTERNATIVE: BATCH FILE SETUP:')
        self.stdout.write('-' * 40)
        
        batch_content = f'''@echo off
cd /d "{settings.BASE_DIR}"
python manage.py reset_monthly_counts
echo Monthly reset completed at %date% %time% >> monthly_reset.log
pause
'''
        
        batch_file_path = os.path.join(settings.BASE_DIR, 'monthly_reset.bat')
        
        try:
            with open(batch_file_path, 'w') as f:
                f.write(batch_content)
            
            self.stdout.write(f'Created batch file: {batch_file_path}')
            self.stdout.write('You can:')
            self.stdout.write('- Double-click to run manually')
            self.stdout.write('- Schedule it in Task Scheduler')
            self.stdout.write('- Add to startup folder for regular execution')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Could not create batch file: {e}'))
        
        self.stdout.write('\n\n4. TESTING:')
        self.stdout.write('-' * 15)
        self.stdout.write('Test the reset command:')
        self.stdout.write(f'   python "{manage_py_path}" reset_monthly_counts --dry-run')
        
        self.stdout.write('\n\n5. MONITORING:')
        self.stdout.write('-' * 18)
        self.stdout.write('Check blocked users in admin:')
        self.stdout.write('   http://127.0.0.1:8000/admin/donation/blockedprofiles/')
        
        self.stdout.write('\n\n6. LOGS:')
        self.stdout.write('-' * 10)
        self.stdout.write('Monthly reset logs will be saved to:')
        self.stdout.write(f'   {os.path.join(settings.BASE_DIR, "monthly_reset.log")}')
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('Setup instructions complete!'))
        self.stdout.write('Run the commands above to test and schedule monthly resets.')