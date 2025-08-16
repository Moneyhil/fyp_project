from django.contrib import admin
from .models import User
from django.contrib.auth.hashers import make_password

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'is_verified', 'created_at')
    list_display_links = ('name', 'email')
    search_fields = ('name', 'email')
    list_filter = ('is_verified',)

    def save_model(self, request, obj, form, change):
        if 'password' in form.changed_data:
            raw_password = form.cleaned_data['password']
            # Hash only if it's not already hashed
            if not raw_password.startswith("pbkdf2_"):
                obj.password = make_password(raw_password)
        super().save_model(request, obj, form, change)
