from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField, UserCreationForm

from profiles.models import HealthcareUser, HealthcareProvince


class ProvinceAdmin(admin.ModelAdmin):
    list_display = ["id", "abbr", "name"]

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
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
    list_display = ("email", "name", "province", "is_admin", "is_superuser")
    list_filter = ("is_admin", "is_superuser")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("name", "province", "phone_number")}),
        ("Permissions", {"fields": ("is_admin", "is_superuser")}),
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


admin.site.register(HealthcareProvince, ProvinceAdmin)
admin.site.register(HealthcareUser, UserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)
