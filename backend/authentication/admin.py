from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "role",
            "department",
            "program",
            "phone_number",
        )


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "role",
            "department",
            "program",
            "phone_number",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
        )


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    list_display = (
        "email",
        "username",
        "full_name",
        "role",
        "department",
        "is_active",
        "created_at",
    )
    list_filter = ("role", "is_active", "department", "program")
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("-created_at",)

    fieldsets = (
        (
            "Informations personnelles",
            {
                "fields": (
                    "username",
                    "email",
                    "first_name",
                    "last_name",
                    "phone_number",
                    "password",
                )
            },
        ),
        (
            "Rôle et permissions",
            {
                "fields": (
                    "role",
                    "department",
                    "program",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                )
            },
        ),
        (
            "Permissions avancées",
            {
                "fields": ("groups", "user_permissions"),
                "classes": ("collapse",),
            },
        ),
        (
            "Dates importantes",
            {
                "fields": ("last_login", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "first_name",
                    "last_name",
                    "role",
                    "department",
                    "program",
                    "phone_number",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                ),
            },
        ),
    )

    readonly_fields = ("created_at", "updated_at")

    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = "Nom complet"
