from imports.constants import Constants
from imports.models.user import User
from imports.response import Response
from imports.table import Table
from lib.cutomjtw import CustomJWT
from util.util import Util

"""
__author__      = Umair Ansari
__copyright__   = Copyright 2007, Cielo WiGle
__date__        = 25, April 2017
__version__     = 1.0.0
"""


def lambda_handler(event, context):
    """
    
    :param event: [user_id, old_password, new_password, confirm_new_password, token]
    :param context: [] 
    :return: 200, 500, 400
    """
    user_id = event.get(User.USER_ID, "").strip()
    old_password = event.get(User.PASSWORD, "").strip()
    new_password = event.get('new_password', "").strip()
    token = event.get('token', "")

    response = Response()
    users_table = Table(User.USER_TABLE)
    if users_table.get_table_object() is None:
        raise Exception(response.get_custom_exception(Constants.SERVER_ERROR, Constants.SERVER_ERROR))

    if user_id != "" and old_password != "" and new_password != "":
        return change_password(user_id, new_password, users_table, response, old_password)

    if new_password != "" and token != "":
        payload = CustomJWT.decode_token(token, Constants.JWT_SECRET, Constants.JWT_ALGO)
        if payload is not None:
            user_id = payload[User.USER_ID]
            return change_password(user_id, new_password, users_table, response)
        return Exception(response.get_custom_exception(Constants.BAD_REQUEST, Constants.NOT_FOUND))
    raise Exception(response.get_custom_exception(Constants.BAD_REQUEST, Constants.INVALID_JSON_FORMAT))


def change_password(user_id, new_password, users_table, response, old_password=None):
    users = users_table.get_item_by_key({User.USER_ID: user_id})

    if old_password is not None:
        if old_password != Util().decode_base64(users.get(User.PASSWORD, "")):
            raise Exception(response.get_custom_exception(Constants.CONFLICT, Constants.USERNAME_PASSWORD_MISMATCH))

    if users is not None:
        if users_table.update_item_by_key({User.USER_ID: user_id}, "set password = :pass", {':pass': Util().encode_base64(new_password)}, "UPDATED_NEW") is not None:
            return response.get_response(Constants.SUCCESS, Constants.SUCCESS)
        raise Exception(response.get_custom_exception(Constants.SERVER_ERROR, Constants.SERVER_ERROR))
    raise Exception(response.get_custom_exception(Constants.CONFLICT, Constants.USERNAME_PASSWORD_MISMATCH))
