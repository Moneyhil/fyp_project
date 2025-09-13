from django.core.management.base import BaseCommand
import subprocess
from pathlib import Path

class Command(BaseCommand):
    help = 'Setup Windows Task Scheduler for monthly donation count reset'

    def add_arguments(self, parser):
        parser.add_argument(
            '--remove',
            action='store_true',
            help='Remove the scheduled task instead of creating it',
        )
        parser.add_argument(
            '--task-name',
            type=str,
            default='DonationMonthlyReset',
            help='Name for the scheduled task (default: DonationMonthlyReset)',
        )

    def handle(self, *args, **options):
        task_name = options['task_name']
        
        if options['remove']:
            self.remove_task(task_name)
        else:
            self.create_task(task_name)

    def remove_task(self, task_name):
        """Remove the scheduled task."""
        try:
            cmd = f'schtasks /delete /tn "{task_name}" /f'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully removed task "{task_name}"')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'Failed to remove task: {result.stderr}')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error removing task: {e}')
            )

    def create_task(self, task_name):
        """Create a Windows scheduled task for monthly reset."""
        # Get current project directory
        project_dir = Path(__file__).parent.parent.parent.parent
        manage_py = project_dir / 'manage.py'
        
        
        python_exe = subprocess.check_output('where python', shell=True, text=True).strip().split('\n')[0]
        
    
        command = f'"{python_exe}" "{manage_py}" monthly_reset_job'
        
        
        schtasks_cmd = [
            'schtasks', '/create',
            '/tn', task_name,
            '/tr', command,
            '/sc', 'monthly',
            '/d', '1',  
            '/st', '00:01',  
            '/f'  
        ]
        
        try:
            self.stdout.write('Creating Windows scheduled task...')
            self.stdout.write(f'Task name: {task_name}')
            self.stdout.write(f'Command: {command}')
            self.stdout.write(f'Schedule: Monthly on 1st day at 00:01')
            
            result = subprocess.run(schtasks_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.stdout.write(
                    self.style.SUCCESS('Successfully created scheduled task!')
                )
                self.stdout.write('\nTask details:')
                self.stdout.write(f'  Name: {task_name}')
                self.stdout.write(f'  Command: {command}')
                self.stdout.write(f'  Schedule: Monthly on 1st at 00:01')
                self.stdout.write(f'  User: SYSTEM')
                
                
                self.stdout.write('\nTask management commands:')
                self.stdout.write(f'  View task: schtasks /query /tn "{task_name}"')
                self.stdout.write(f'  Run now: schtasks /run /tn "{task_name}"')
                self.stdout.write(f'  Delete task: python manage.py setup_windows_scheduler --remove')
                
            else:
                self.stdout.write(
                    self.style.ERROR(f'Failed to create task: {result.stderr}')
                )
                self.stdout.write(f'Command used: {" ".join(schtasks_cmd)}')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating task: {e}')
            )

    def get_task_info(self, task_name):
        """Get information about the scheduled task."""
        try:
            cmd = f'schtasks /query /tn "{task_name}" /fo LIST /v'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                return result.stdout
            else:
                return None
        except Exception:
            return None