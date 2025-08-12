from django.contrib import admin
from .models import Admin1, Registration
from django.contrib.auth.hashers import make_password

@admin.register(Admin1)
class Admin1Admin(admin.ModelAdmin):
    list_display = ('first_name', 'email', 'phone_number')


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'is_verified')  # Removed password
    list_display_links = ('email',)                  # Click email to edit
    search_fields = ('name', 'email')                # Search by name/email
    list_filter = ('is_verified',)                   # Filter by verification

    def save_model(self, request, obj, form, change):
        if 'password' in form.changed_data:
            obj.password = make_password(form.cleaned_data['password'])  # Re-hash on edit
        super().save_model(request, obj, form, change)

