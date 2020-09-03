from django import forms
from django.contrib import admin
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField, UserCreationForm
from django.contrib.admin.templatetags.admin_list import _boolean_icon

from profiles.models import HealthcareUser, HealthcareProvince, AuthorizedDomain


class ProvinceAdmin(admin.ModelAdmin):
    list_display = ["id", "abbr", "name", "is_api_key_set"]
    readonly_fields = [
        "abbr",
        "name",
    ]

    def is_api_key_set(self, obj: "HealthcareProvince"):
        if obj.api_key is None:
            return _boolean_icon(False)
        return _boolean_icon(True)

    is_api_key_set.short_description = _("Has a bearer token")

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = HealthcareUser
        fields = (
            "email",
            "password",
            "name",
            "province",
            "is_active",
            "is_admin",
            "is_superuser",
            "phone_number",
            "blocked_until",
        )

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserAddForm(UserCreationForm):
    """A form for creating new users. Extends from UserCreationForm form, which
    means it includes a repeated password."""

    class Meta:
        model = HealthcareUser
        fields = (
            "email",
            "name",
            "province",
            "is_admin",
            "is_superuser",
            "phone_number",
        )

    def clean_email(self):
        email = self.cleaned_data.get("email", "").lower()
        return email


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserAddForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = (
        "email",
        "name",
        "province",
        "is_active",
        "is_admin",
        "is_superuser",
        "number_keys_generated",
    )
    list_filter = (
        "is_admin",
        "is_superuser",
        "is_active",
    )

    def number_keys_generated(self, user: HealthcareUser):
        return user.covidkey_set.filter(
            created_at__gte=(timezone.now() - timedelta(hours=24))
        ).count()

    number_keys_generated.short_description = _(
        "Number of keys generated in the last 24 hours"
    )

    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "name",
                    "province",
                    "password1",
                    "password2",
                    "phone_number",
                ),
            },
        ),
        ("Permissions", {"fields": ("is_admin", "is_superuser")}),
    )
    search_fields = ("email",)
    ordering = ("email",)
    filter_horizontal = ()

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets

        permissions_tuple = (
            "Permissions",
            {"fields": ("is_admin", "is_superuser", "is_active", "blocked_until")},
        )
        fieldsets = (
            (None, {"fields": ("email", "password")}),
            ("Personal info", {"fields": ("name", "province", "phone_number")}),
        )
        if request.user.is_superuser and obj.id != request.user.id:
            fieldsets += (permissions_tuple,)
        return fieldsets


admin.site.register(HealthcareProvince, ProvinceAdmin)
admin.site.register(HealthcareUser, UserAdmin)
admin.site.register(AuthorizedDomain)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)
