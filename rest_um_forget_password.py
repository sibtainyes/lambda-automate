import json

from boto3.dynamodb.conditions import Key
from imports.models.user import User
from imports.constants import Constants
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

    :param event: 
    :param context: 
    :return: 
    """
    email_id = event.get(User.EMAIL_ID, "")
    base_url = event.get('base_url', "")
    response = Response()
    if email_id != "" and base_url != "":
        user_table = Table(User.USER_TABLE)
        user = user_table.get_item_via_query(Key(User.EMAIL_ID).eq(email_id), User.USER_EMAIL_INDEX)[0]
        if user is not None:
            user_id = user[User.USER_ID]
            is_social_media = user.get(User.IS_SOCIAL_MEDIA, 0)
            encoded_token = CustomJWT().get_token_with_email(user_id, email_id, Constants.JWT_ONE_DAY, Constants.JWT_SECRET, Constants.JWT_ALGO)
            Util().send_email_forget_password(email_id, base_url, encoded_token, is_social_media, user_id)

            result = user_table.update_item_by_key(
                {User.USER_ID: user_id},
                'SET encoded_token = :encoded_token, token_is_valid = :token_is_valid',
                {':encoded_token': encoded_token, ':token_is_valid': 1},
                "UPDATED_NEW"
            )
            if result is not None:
                return response.get_response(Constants.SUCCESS, Constants.SUCCESS)
            raise Exception(response.get_custom_exception(Constants.SERVER_ERROR, Constants.SERVER_ERROR))
        raise Exception(response.get_custom_exception(Constants.NOT_FOUND, Constants.NOT_FOUND))
    raise Exception(response.get_custom_exception(Constants.BAD_REQUEST, Constants.INVALID_JSON_FORMAT))
