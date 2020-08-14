import logging
from logging import getLogger
from datetime import datetime
from easyaudit.models import CRUDEvent
import json

logger = getLogger("easyaudit_logging")
logger.setLevel(logging.INFO)


class LoggerBackend:
    def request(self, request_info):
        # The Amazon WAF already logs requests info, no need to send them again
        return request_info

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
        return login_info

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

        model = json.loads(crud_info.get("object_json_repr"))[0].get("model")
        changed_fields_data = json.loads(crud_info.get("changed_fields", "{}"))
        if changed_fields_data is not None:
            changed_fields = list(changed_fields_data.keys())
        else:
            changed_fields = []
        # datetime CRUD event_type obj_name obj_id user_id remote_ip
        logger.info(
            msg=f'{crud_info.get("datetime")} CRUD event_type:{event_type} model:{model} object_id:{crud_info.get("object_id")} fields_changed:{",".join(changed_fields)} user_id:{crud_info.get("user_id")}',
            extra=crud_info,
        )
        return crud_info
