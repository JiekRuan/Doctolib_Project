from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from hms.models import User
from django.utils.translation import gettext_lazy as _


# Register your models here.
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', "phone_number", "role", "doctor", 'is_staff', "created_at", 'id')
    list_filter = ('role', 'doctor')

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name",)}),
        (_("Custom info"), {"fields": ("role", "doctor", "phone_number", "csv_upload_date", "csv_data")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )
    search_fields = ('email',)
    ordering = ('created_at',)


admin.site.register(User, CustomUserAdmin)
