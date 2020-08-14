import logging
from logging import getLogger
from datetime import datetime
from easyaudit.models import CRUDEvent


class LoggerBackend:
    logger = getLogger("easyaudit_logging")
    logger.setLevel(logging.DEBUG)

    def request(self, request_info):
        # Django already logs requests info, no need to send them again
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
        self.logger.info(
            msg=f'{datetime.utcnow()} LOGIN {login_types.get(login_info.get("login_type"), "other")} {login_info.get("user_id")}::{login_info.get("remote_ip")}',
            extra=login_info,
        )
        return login_info

    def crud(self, crud_info):
        event_type = None
        if crud_info.event_type == CRUDEvent.CREATE:
            event_type = 'CREATE'
        if crud_info.event_type == CRUDEvent.UPDATE:
            event_type = 'UPDATE'
        if crud_info.event_type == CRUDEvent.DELETE:
            event_type = 'DELETE'

        if event_type is None:
            # That means the event is either m2m_change or m2m_rev_change, which we don't care about
            return crud_info

        # datetime CRUD event_type obj_name obj_id user_id remote_ip
        self.logger.info(msg=f'{crud_info.get("datetime")} CRUD {event_type}  ', extra=crud_info)
        return crud_info
