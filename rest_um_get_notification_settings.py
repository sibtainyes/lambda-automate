from imports.models.installations import Installations
from imports.models.user import User
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
    mobile_device_id = event.get(Installations.MOBILE_DEVICE_ID, "").strip()
    response = Response()
    if user_id != "" and mobile_device_id != "":
        installations_table = Table(Installations.INSTALLATIONS_TABLE)
        installations = installations_table.get_item_by_key({User.USER_ID: user_id, Installations.MOBILE_DEVICE_ID: mobile_device_id})
        notification_settings = None
        if installations is not None:
            notification_settings = {"is_enabled": str(installations[Installations.NOTIFICATION_BLOCKED])}
        return response.get_response(Constants.SUCCESS, Constants.SUCCESS, notification_settings)
    raise Exception(response.get_custom_exception(Constants.BAD_REQUEST, Constants.INVALID_JSON_FORMAT))
