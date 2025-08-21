@echo off
cd /d "D:\app\fyp_project\backend\djangobackend"
python manage.py reset_monthly_counts
echo Monthly reset completed at %date% %time% >> monthly_reset.log
pause
