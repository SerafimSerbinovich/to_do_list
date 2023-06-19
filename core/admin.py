from core.models import User
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    readonly_fields = ("last_login", "date_joined")
    fieldsets = (
        (None, {"fields": ("username",)}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        ("Permissions", {
                "fields": (
                    "is_active",
                    "is_staff",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    list_display = ("username", "email", "first_name", "last_name")
    list_filter = ("is_staff", "is_superuser", "is_active")

admin.site.unregister(Group)
