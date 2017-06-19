import json

from imports.models.user import User

from imports.models.installations import Installations
from imports.constants import Constants
from imports.response import Response
from imports.table import Table

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
    is_enabled = event.get('is_enabled', "")
    mobile_device_id = event.get(Installations.MOBILE_DEVICE_ID, "").strip()

    response = Response()

    if user_id != "" and mobile_device_id != "" and isinstance(is_enabled, int):
        installations_table = Table(Installations.INSTALLATIONS_TABLE)
        installations = installations_table.get_item_by_key({User.USER_ID: user_id, Installations.MOBILE_DEVICE_ID: mobile_device_id})
        if installations is not None:
            rs = installations_table.update_item_by_key(
                {User.USER_ID: user_id, Installations.MOBILE_DEVICE_ID: mobile_device_id},
                "SET notification_blocked = :notification_blocked",
                {':notification_blocked': is_enabled},
                "UPDATED_NEW")
            if rs is not None:
                return response.get_response(Constants.SUCCESS, Constants.SUCCESS)
            raise Exception(response.get_custom_exception(Constants.NOT_FOUND, Constants.NOT_FOUND))
        else:
            return response.get_response(Constants.SUCCESS, Constants.SUCCESS)
    raise Exception(response.get_custom_exception(Constants.BAD_REQUEST, Constants.INVALID_JSON_FORMAT))
