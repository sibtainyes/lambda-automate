from imports.models.central_system import CentralSystem
from imports.models.user import User
from imports.constants import Constants
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
            central_sys = Table(CentralSystem.CENTRAL_SYSTEM_TABLE).get_item_by_key({'id': 1})
            bucket_name = central_sys[CentralSystem.BUCKET_NAME] if central_sys is not None else None
            user_image = ""
            if user.get(User.USER_IMAGE_PATH, None) is not None and bucket_name is not None:
                user_image = Util().get_bucket_image_path(bucket_name, user[User.USER_IMAGE_PATH])
            response_object = {
                User.USER_IMAGE_PATH: user_image
            }
            return response.get_response(Constants.SUCCESS, Constants.SUCCESS, response_object)
    raise Exception(response.get_custom_exception(Constants.BAD_REQUEST, Constants.INVALID_JSON_FORMAT))
