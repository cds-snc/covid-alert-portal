import logging
from datetime import datetime


class LoggerBackend:
    logging.basicConfig()
    logger = logging.getLogger("easyaudit_logging")
    logger.setLevel(logging.DEBUG)

    def request(self, request_info):
        self.logger.debug(
            msg=f'{request_info.get("datetime")}::REQUEST::{request_info.get("url")}::{request_info.get("remote_ip")}',
            extra=request_info,
        )
        return request_info  # if you don't need it

    def login(self, login_info):
        # LOGIN = 0
        # LOGOUT = 1
        # FAILED = 2
        login_types = {
            0: "login",
            1: "logout",
            2: "failed",
        }
        self.logger.info(
            msg=f'{datetime.utcnow()}::LOGIN::{login_types.get(login_info.get("login_type"), "other")}-{login_info.get("user_id")}::{login_info.get("remote_ip")}',
            extra=login_info,
        )
        return login_info

    def crud(self, crud_info):
        # CREATE = 1
        # UPDATE = 2
        # DELETE = 3
        # M2M_CHANGE = 4
        # M2M_CHANGE_REV = 5
        self.logger.info(msg=f'{crud_info.get("datetime")}::CRUD::', extra=crud_info)
        return crud_info
