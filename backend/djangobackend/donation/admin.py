from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'name', 'is_staff', 'date_joined', 'is_verified')  # Use date_joined instead of created_at
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_verified')
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

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'contact_number', 'city', 'blood_group', 'role', 'created_at')
    list_filter = ('gender', 'blood_group', 'role', 'city', 'created_at')
    search_fields = ('user__email', 'user__name', 'first_name', 'last_name', 'contact_number')
    ordering = ('-created_at',)
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

admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)