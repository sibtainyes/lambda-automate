from imports.models.user import User
from imports.constants import Constants
from imports.response import Response
from imports.table import Table
from lib.cutomjtw import CustomJWT


"""
__author__      = Umair Ansari
__copyright__   = Copyright 2007, Cielo WiGle
__date__        = 8, May 2017
__version__     = 1.0.0
"""


def lambda_handler(event, context):
    """
    :param event: [token]
    :param context: []
    :return: 404, 200
    """
    token = event.get('token', "")
    response = Response()
    if token != "":
        payload = CustomJWT().decode_token(token, Constants.JWT_SECRET, Constants.JWT_ALGO)
        if payload is not None:
            user_id = payload[User.USER_ID]
            users_table = Table(User.USER_TABLE)
            if users_table.get_table_object() is None:
                raise Exception(response.get_custom_exception(Constants.SERVER_ERROR, Constants.SERVER_ERROR))
            user = users_table.get_item_by_key({User.USER_ID: user_id})
            if user is not None:
                encoded_token = user.get(User.ENCODED_TOKEN, "")
                token_is_valid = user.get(User.TOKEN_IS_VALID, "")
                if encoded_token == token and token_is_valid == 1:
                    return response.get_response(Constants.SUCCESS, Constants.SUCCESS)
    raise Exception(response.get_custom_exception(Constants.NOT_FOUND, Constants.NOT_FOUND))
