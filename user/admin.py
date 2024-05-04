from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext as gt

from user.models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    fieldsets = (
        (None,
         {
             "fields": (
                 "first_name", "last_name", "email", "password"
             )
         }
         ),
        (
            gt("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (gt("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("first_name", "last_name", "email", "password")
            },
        ),
    )
    list_display = (
        "first_name", "last_name", "email", "password", "is_active"
    )
    search_fields = ("first_name", "last_name", "email")
    ordering = ("first_name", "last_name", "email")
