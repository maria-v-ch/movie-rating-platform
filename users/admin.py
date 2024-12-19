# pylint: disable=relative-beyond-top-level
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, UserFavoriteMovie


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "is_staff", "date_joined")
    search_fields = ("username", "email")
    ordering = ("-date_joined",)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("email",)}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
    )


@admin.register(UserFavoriteMovie)
class UserFavoriteMovieAdmin(admin.ModelAdmin):
    list_display = ("user", "movie", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "movie__title")
    ordering = ("-created_at",)
