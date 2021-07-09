from functools import partial

from django import forms
from django.contrib import admin, messages
from datetime import timedelta
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Permission
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField, UserCreationForm
from django.contrib.admin.templatetags.admin_list import _boolean_icon

from profiles.models import HealthcareUser, HealthcareProvince, AuthorizedDomain
from register.admin import SurveySentFilter as RegisterSurveySentFilter
from register.models import Survey, HealthcareUserSurvey
from register.forms import send_email


class ProvinceAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "abbr",
        "name",
        "sms_enabled",
        "qr_code_enabled",
        "is_api_key_set",
    ]
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
    can_send_alerts = forms.BooleanField(
        label=_("Allow user to send outbreak alerts"), required=False
    )

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
            "can_send_alerts",
            "phone_number",
            "blocked_until",
        )

    def __init__(self, *args, **kwargs):
        if "instance" in kwargs:
            user = kwargs["instance"]
            initial = {"can_send_alerts": user.has_perm("profiles.can_send_alerts")}
            kwargs["initial"] = initial
        super().__init__(*args, **kwargs)

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

    def save(self, commit=True):
        # Save the custom permission
        user = super().save(commit=False)
        permission = Permission.objects.get(codename="can_send_alerts")
        if self.cleaned_data["can_send_alerts"]:
            user.user_permissions.add(permission)
        else:
            user.user_permissions.remove(permission)
        if commit:
            user.save()
        return user


class UserAddForm(UserCreationForm):
    """A form for creating new users. Extends from UserCreationForm form, which
    means it includes a repeated password."""

    can_send_alerts = forms.BooleanField(
        label=_("Allow user to send outbreak alerts"), required=False
    )

    class Meta:
        model = HealthcareUser
        fields = (
            "email",
            "name",
            "province",
            "is_admin",
            "is_superuser",
            "can_send_alerts",
            "phone_number",
        )

    def clean_email(self):
        email = self.cleaned_data.get("email", "").lower()
        return email

    def save(self, commit=True):
        # Save the custom permission
        user = super().save(commit=False)
        permission = Permission.objects.get(codename="can_send_alerts")
        if self.cleaned_data["can_send_alerts"]:
            user.user_permissions.add(permission)
        else:
            user.user_permissions.remove(permission)
        if commit:
            user.save()
        return user


class SurveySentFilter(RegisterSurveySentFilter):
    def queryset(self, request, queryset):
        if self.value() == "none":
            return queryset.exclude(healthcareusersurvey__healthcare_user__in=queryset)
        elif self.value() == "all":
            surveys = Survey.objects.all()
            for survey in surveys:
                queryset = queryset.filter(
                    healthcareusersurvey__healthcare_user__in=queryset,
                    healthcareusersurvey__survey=survey,
                )
            return queryset.distinct()
        elif self.value():
            id, code = self.value().split(":")
            if code == "0":
                return queryset.exclude(healthcareusersurvey__survey_id=id)
            elif code == "1":
                return queryset.filter(healthcareusersurvey__survey_id=id).distinct()


class SentAlertFilter(admin.SimpleListFilter):
    title = _("Sent an alert")
    parameter_name = "sentalert"

    def lookups(self, request, model_admin):
        return (("yes", "Yes"), ("no", "No"))

    def queryset(self, request, queryset):
        if self.value():
            created = self.value() == "yes"
            return queryset.filter(
                notification__created_by__isnull=not created
            ).distinct()


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
        "can_send_alerts",
        "number_keys_generated",
        "surveys",
    )
    list_filter = (
        "is_admin",
        "is_superuser",
        "is_active",
        "province",
        SentAlertFilter,
        SurveySentFilter,
    )

    def can_send_alerts(self, user: HealthcareUser):
        return user.has_perm("profiles.can_send_alerts")

    can_send_alerts.boolean = True

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
        ("Permissions", {"fields": ("is_admin", "is_superuser", "can_send_alerts")}),
    )
    search_fields = ("email",)
    ordering = ("email",)
    filter_horizontal = ()

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets

        permissions_tuple = (
            "Permissions",
            {
                "fields": (
                    "is_admin",
                    "is_superuser",
                    "is_active",
                    "blocked_until",
                    "can_send_alerts",
                )
            },
        )
        fieldsets = (
            (None, {"fields": ("email", "password")}),
            ("Personal info", {"fields": ("name", "province", "phone_number")}),
        )
        if request.user.is_superuser and obj.id != request.user.id:
            fieldsets += (permissions_tuple,)
        return fieldsets

    def surveys(self, obj):
        surveys = Survey.objects.all()
        val = ""
        count = 0
        for survey in surveys:
            delimiter = "" if count == 0 else ", "
            healthcare_user_surveys = HealthcareUserSurvey.objects.filter(
                healthcare_user=obj, survey=survey
            )
            if healthcare_user_surveys:
                count += 1
                val += f"{delimiter}{survey}"
        return val

    def get_actions(self, request):
        actions = super().get_actions(request)
        surveys = Survey.objects.all()
        for survery in surveys:
            sender_func = partial(self.send_survey_by_id, survery.id)
            actions[f"survey_{survery.id}"] = (
                sender_func,
                f"survey_{survery.id}",
                f"Immediately email {survery} to healthcare user(s)",
            )
        return actions

    @staticmethod
    def send_survey_by_id(id, modeladmin, request, queryset):
        count = 0
        for healthcare_user in queryset:
            if not healthcare_user.notification_set.exists():
                modeladmin.message_user(
                    request,
                    _(f"{healthcare_user.email} has not sent an alert."),
                    messages.WARNING,
                )
            else:
                reg_surveys = healthcare_user.survey_recipient.filter(survey_id=id)
                if reg_surveys:
                    modeladmin.message_user(
                        request,
                        _(
                            f"{healthcare_user.email} has already had this survey sent to them."
                        ),
                        messages.WARNING,
                    )
                else:
                    reg_survey = HealthcareUserSurvey.objects.create(
                        healthcare_user=healthcare_user,
                        survey_id=id,
                        sent_by=request.user,
                        sent_ts=timezone.now(),
                    )
                    try:
                        survey = reg_survey.survey
                        template_id = (
                            survey.en_notify_template_id
                            if healthcare_user.language_cd == "en"
                            else survey.fr_notify_template_id
                        )
                        send_email(
                            healthcare_user.email,
                            {"url": survey.url},
                            template_id,
                        )
                        count += 1
                    except Exception as e:
                        modeladmin.message_user(
                            request,
                            _(f"{str(e)} :: email: {healthcare_user.email}"),
                            messages.ERROR,
                        )
                        reg_survey.delete()
        if count:
            modeladmin.message_user(
                request, _(f"Sent {count} messages successfully"), messages.SUCCESS
            )


admin.site.register(HealthcareProvince, ProvinceAdmin)
admin.site.register(HealthcareUser, UserAdmin)
admin.site.register(AuthorizedDomain)
admin.site.register(Survey)
