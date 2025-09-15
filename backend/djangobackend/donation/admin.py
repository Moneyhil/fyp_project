from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.db.models import Q
from .models import User, Profile, Admin, MonthlyDonationTracker

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'name', 'is_staff', 'user_status', 'date_joined', 'is_verified')  
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_verified')
    actions = ['block_user_account', 'unblock_user_account', 'delete_user_account']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'name')
    ordering = ('-date_joined',)
    filter_horizontal = ()
    
    def user_status(self, obj):
        if obj.is_staff:
            return format_html('<span style="color: blue; font-weight: bold;">Staff</span>')
        elif obj.is_active:
            return format_html('<span style="color: green; font-weight: bold;">Active</span>')
        else:
            return format_html('<span style="color: red; font-weight: bold;">Blocked</span>')
    user_status.short_description = 'Status'
    
    def block_user_account(self, request, queryset):
        count = 0
        for user in queryset:
            if user.is_active and not user.is_staff:
                user.is_active = False
                user.save()
                count += 1
        
        self.message_user(request, f'Successfully blocked {count} user accounts.')
    block_user_account.short_description = "Block selected user accounts (non-staff only)"
    def unblock_user_account(self, request, queryset):
        from donation.email_config import EmailService
        from django.utils import timezone
        
        count = 0
        email_count = 0
        current_month = timezone.now().strftime('%B %Y')
        
        for user in queryset:
            if not user.is_active and not user.is_staff:
                user.is_active = True
                user.manual_block_override = True  # Add this line
                user.save()
                count += 1
                
                try:
                    success, message = EmailService.send_monthly_unblock_notification(user, current_month)
                    if success:
                        email_count += 1
                except Exception as e:
                    pass  
        
        message = f'Successfully unblocked {count} user accounts with manual override.'
        if email_count > 0:
            message += f' Sent {email_count} notification emails.'
        self.message_user(request, message)
    unblock_user_account.short_description = "Unblock selected user accounts (non-staff only)"
    
    def delete_user_account(self, request, queryset):
        from django.contrib import messages
        
        count = 0
        for user in queryset:
            if not user.is_staff:  
                try:
                    user_email = user.email
                    user.delete()
                    count += 1
                except Exception as e:
                    messages.error(request, f'Failed to delete user {user.email}: {str(e)}')
            else:
                messages.warning(request, f'Cannot delete staff user: {user.email}')
        
        if count > 0:
            self.message_user(request, f'Successfully deleted {count} user accounts.')
    delete_user_account.short_description = "Delete selected user accounts (non-staff only)"

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'contact_number', 'city', 'blood_group', 'role', 'user_status', 'created_at')
    list_filter = ('gender', 'blood_group', 'role', 'city', 'created_at', 'user__is_active')
    search_fields = ('user__email', 'user__name', 'first_name', 'last_name', 'contact_number')
    ordering = ('-created_at',)
    actions = ['block_user_account', 'unblock_user_account', 'delete_user_and_profile']
    fieldsets = (
        ('User Information', {'fields': ('user',)}),
        ('Personal Details', {'fields': ('first_name', 'last_name', 'contact_number', 'gender')}),
        ('Location', {'fields': ('address', 'city')}),
        ('Medical Information', {'fields': ('blood_group',)}),
        ('Role', {'fields': ('role',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at', 'updated_at')
    
    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Full Name'
    
    def user_status(self, obj):
        if obj.user.is_active:
            return format_html('<span style="color: green; font-weight: bold;">Active</span>')
        else:
            return format_html('<span style="color: red; font-weight: bold;">Blocked</span>')
    user_status.short_description = 'Account Status'
    
    def block_user_account(self, request, queryset):
        count = 0
        for profile in queryset:
            user = profile.user
            if user.is_active:
                user.is_active = False
                user.save()
                count += 1
        
        self.message_user(request, f'Successfully blocked {count} user accounts.')
    block_user_account.short_description = "Block selected user accounts"
    
    def unblock_user_account(self, request, queryset):
        from donation.email_config import EmailService
        from django.utils import timezone
        
        count = 0
        email_count = 0
        current_month = timezone.now().strftime('%B %Y')
        
        for profile in queryset:
            user = profile.user
            if not user.is_active:
                user.is_active = True
                user.save()
                count += 1
                
                
                try:
                    success, message = EmailService.send_monthly_unblock_notification(user, current_month)
                    if success:
                        email_count += 1
                except Exception as e:
                    pass  
        
        message = f'Successfully unblocked {count} user accounts.'
        if email_count > 0:
            message += f' Sent {email_count} notification emails.'
        self.message_user(request, message)
    unblock_user_account.short_description = "Unblock selected user accounts"
    
    def delete_user_and_profile(self, request, queryset):
        
        from django.contrib import messages
        
        count = 0
        for profile in queryset:
            user = profile.user
            try:
                
                user_email = user.email
                user.delete()
                count += 1
            except Exception as e:
                messages.error(request, f'Failed to delete user {user.email}: {str(e)}')
        
        if count > 0:
            self.message_user(request, f'Successfully deleted {count} user profiles and accounts.')
    delete_user_and_profile.short_description = "Delete selected user profiles"

class AdminAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'is_active', 'is_superuser', 'date_joined')
    list_filter = ('is_active', 'is_superuser', 'date_joined')
    search_fields = ('email', 'name')
    ordering = ('-date_joined',)
    fieldsets = (
        ('Admin Information', {'fields': ('email', 'name', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_superuser')}),
        ('Timestamps', {'fields': ('date_joined', 'last_login'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('date_joined', 'last_login')
    
    def save_model(self, request, obj, form, change):
        if not change:  
            obj.set_password(obj.password)
        super().save_model(request, obj, form, change)

class MonthlyDonationTrackerAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_email', 'month', 'completed_calls_count', 'monthly_goal_completed', 'goal_completed_at', 'is_blocked')
    list_filter = ('monthly_goal_completed', 'month', 'completed_calls_count')
    search_fields = ('user__email', 'user__name')
    ordering = ('-month', '-completed_calls_count')
    readonly_fields = ('created_at', 'updated_at')
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    
    def is_blocked(self, obj):
        if obj.monthly_goal_completed and obj.completed_calls_count >= 3:
            return format_html('<span style="color: red; font-weight: bold;">BLOCKED</span>')
        return format_html('<span style="color: green;">Active</span>')
    is_blocked.short_description = 'Status'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')

class BlockedProfilesAdmin(admin.ModelAdmin):
    
    list_display = ('user', 'user_email', 'month', 'completed_calls_count', 'goal_completed_at', 'user_status', 'is_current_month')
    list_filter = ('month', 'goal_completed_at', 'monthly_goal_completed')
    search_fields = ('user__email', 'user__name')
    ordering = ('-goal_completed_at',)
    actions = ['reset_monthly_count', 'block_user_account', 'unblock_user_account', 'delete_user_profile']
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    
    def user_status(self, obj):
        from django.utils import timezone
        current_month = timezone.now().date().replace(day=1)
        if obj.month == current_month and obj.monthly_goal_completed:
            return format_html('<span style="color: red; font-weight: bold;">BLOCKED (Current Month)</span>')
        elif obj.monthly_goal_completed:
            return format_html('<span style="color: orange; font-weight: bold;">BLOCKED (Past Month)</span>')
        return format_html('<span style="color: green;">Active</span>')
    user_status.short_description = 'Status'
    
    def is_current_month(self, obj):
        from django.utils import timezone
        current_month = timezone.now().date().replace(day=1)
        if obj.month == current_month:
            return format_html('<span style="color: red; font-weight: bold;">YES</span>')
        return format_html('<span style="color: gray;">NO</span>')
    is_current_month.short_description = 'Current Month?'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(
            monthly_goal_completed=True,
            completed_calls_count__gte=3
        ).select_related('user')
    
    def reset_monthly_count(self, request, queryset):
        from django.utils import timezone
        current_month = timezone.now().date().replace(day=1)
        
        count = 0
        for tracker in queryset:
            if tracker.month == current_month:
                tracker.reset_for_new_month()
                count += 1
        
        self.message_user(request, f'Successfully reset {count} monthly trackers for current month.')
    reset_monthly_count.short_description = "Reset monthly count for current month"
    
    def has_add_permission(self, request):
        
        return False
    
    def block_user_account(self, request, queryset):
        
        count = 0
        for tracker in queryset:
            user = tracker.user
            if user.is_active:
                user.is_active = False
                user.save()
                count += 1
        
        self.message_user(request, f'Successfully blocked {count} user accounts.')
    block_user_account.short_description = "Block selected user accounts"
    
    def unblock_user_account(self, request, queryset):
        from donation.email_config import EmailService
        from django.utils import timezone
        
        count = 0
        email_count = 0
        current_month = timezone.now().strftime('%B %Y')
        
        for tracker in queryset:
            user = tracker.user
            if not user.is_active:
                user.is_active = True
                user.save()
                count += 1
                
        
                try:
                    success, message = EmailService.send_monthly_unblock_notification(user, current_month)
                    if success:
                        email_count += 1
                except Exception as e:
                    pass  
        message = f'Successfully unblocked {count} user accounts.'
        if email_count > 0:
            message += f' Sent {email_count} notification emails.'
        self.message_user(request, message)
    unblock_user_account.short_description = "Unblock selected user accounts"
    
    def delete_user_profile(self, request, queryset):
        
        from django.contrib import messages
        
        count = 0
        for tracker in queryset:
            user = tracker.user
            try:
                user_email = user.email
                user.delete()
                count += 1
            except Exception as e:
                messages.error(request, f'Failed to delete user {user.email}: {str(e)}')
        
        if count > 0:
            self.message_user(request, f'Successfully deleted {count} user profiles and accounts.')
    delete_user_profile.short_description = "Delete selected user profiles"
    
    def has_delete_permission(self, request, obj=None):
        
        return False

admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Admin, AdminAdmin)
admin.site.register(MonthlyDonationTracker, MonthlyDonationTrackerAdmin)

class BlockedProfiles(MonthlyDonationTracker):
    class Meta:
        proxy = True
        verbose_name = 'Blocked Profile'
        verbose_name_plural = 'Blocked Profiles'

admin.site.register(BlockedProfiles, BlockedProfilesAdmin)