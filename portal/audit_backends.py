from logging import getLogger
from datetime import datetime
from easyaudit.models import RequestEvent, CRUDEvent, LoginEvent
from profiles.models import HealthcareProvince
from django.db.models import Count, Q
import json

logger = getLogger("easyaudit_logging")


class LoggerBackend:
    def request(self, request_info):
        # No need to log into the console for request, the WAF takes care of this
        return RequestEvent.objects.create(**request_info)

    def login(self, login_info):
        # LOGIN = 0
        # LOGOUT = 1
        # FAILED = 2
        login_types = {
            0: "login",
            1: "logout",
            2: "failed",
        }

        # datetime LOGIN login_type obj_name user_id remote_ip
        logger.info(
            msg=f'{datetime.utcnow()} LOGIN login_type:{login_types.get(login_info.get("login_type"), "other")} user_id:{login_info.get("user_id")} remote_ip:{login_info.get("remote_ip")}',
            extra=login_info,
        )
        return LoginEvent.objects.create(**login_info)

    def crud(self, crud_info):
        event_type = None
        if crud_info.get("event_type") == CRUDEvent.CREATE:
            event_type = "CREATE"
        if crud_info.get("event_type") == CRUDEvent.UPDATE:
            event_type = "UPDATE"
        if crud_info.get("event_type") == CRUDEvent.DELETE:
            event_type = "DELETE"

        if event_type is None:
            # That means the event is either m2m_change or m2m_rev_change, which we don't care about
            return crud_info

        crud_info_dict = json.loads(crud_info.get("object_json_repr"))
        model = crud_info_dict[0].get("model")

        changed_fields_data = json.loads(crud_info.get("changed_fields", "{}"))
        if changed_fields_data is not None:
            changed_fields = list(changed_fields_data.keys())
        else:
            changed_fields = []
        # datetime CRUD event_type obj_name obj_id user_id remote_ip

        if model == "profiles.healthcareuser" and (
            event_type == "CREATE" or event_type == "DELETE"
        ):

            portal_users = HealthcareProvince.objects.annotate(
                num_admins=Count(
                    "healthcareuser", filter=Q(healthcareuser__is_admin="True")
                ),
                num_super_admins=Count(
                    "healthcareuser", filter=Q(healthcareuser__is_superuser="True")
                ),
                num_staff=Count(
                    "healthcareuser", filter=Q(healthcareuser__is_admin="False")
                ),
            ).values_list("name", "num_admins", "num_super_admins", "num_staff")

            for users in portal_users:
                logger.info(
                    msg=f'{crud_info.get("datetime")} LOGGING user_count province: "{users[0]}" super_admins: {users[2]} admins: {users[1]}  staff: {users[3]}',
                    extra=crud_info,
                )

        logger.info(
            msg=f'{crud_info.get("datetime")} CRUD event_type:{event_type} model:{model} object_id:{crud_info.get("object_id")} fields_changed:{",".join(changed_fields)} user_id:{crud_info.get("user_id")}',
            extra=crud_info,
        )
        return CRUDEvent.objects.create(**crud_info)
