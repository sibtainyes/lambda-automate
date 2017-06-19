from imports.models.central_system import CentralSystem
from imports.models.user import User
from imports.constants import Constants
from imports.defaults import Defaults
from imports.response import Response
from imports.table import Table
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
    user_id = event.get(User.USER_ID, "").strip()
    response = Response()
    if user_id != "":
        user_table = Table(User.USER_TABLE)
        user = user_table.get_item_by_key({User.USER_ID: user_id})
        if user is None:
            raise Exception(response.get_custom_exception(Constants.NOT_FOUND, Constants.NOT_FOUND))
        else:
            central_sys = Defaults.CENTRAL_SYSTEM[Constants.ENVIRONMENT]
            bucket_name = central_sys[CentralSystem.BUCKET_NAME] if central_sys is not None else None
            user_image_path = None
            if user.get(User.USER_IMAGE_PATH, None) is not None and bucket_name is not None:
                user_image_path = Util().get_bucket_image_path(bucket_name, user[User.USER_IMAGE_PATH])

            response_object = {
                User.USER_ID: user_id,
                User.EMAIL_ID: user[User.EMAIL_ID],
                User.CREATED_AT: user[User.CREATED_AT],
                User.IS_EMAIL_VERIFIED: user[User.IS_EMAIL_VERIFIED],
                User.CONTACT_NO: user[User.CONTACT_NO],
                User.USER_IMAGE_PATH: user_image_path,
                User.CURRENCY_SYMBOL: user.get(User.CURRENCY_SYMBOL, central_sys[CentralSystem.DEFAULT_CURRENCY_SYMBOL])
            }
            return response.get_response(Constants.SUCCESS, Constants.SUCCESS, response_object)
    raise Exception(response.get_custom_exception(Constants.BAD_REQUEST, Constants.INVALID_JSON_FORMAT))
