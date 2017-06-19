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

    :param event: [user_id, device_token_id, mobile_device_id]
    :param context: []
    :return: 200 for success, 400 for missing parameter values, 500 if code crashes, 409 if conflict

    @about: 1. validate all incoming parameters, return 400 if missing
            2. delete entry in installation table against this user, 404 if not found
            3. create and send back response
    """
    user_id = event.get(User.USER_ID, "").strip()
    mobile_device_id = event.get(Installations.MOBILE_DEVICE_ID, "").strip()

    response = Response()

    # 1. validate all incoming parameters, return 400 if missing
    if user_id != "" and mobile_device_id != "":
        # 2. delete entry in installation table against this user, 404 if not found
        if Table(Installations.INSTALLATIONS_TABLE).delete_item_by_key({User.USER_ID: user_id, Installations.MOBILE_DEVICE_ID: mobile_device_id}, Constants.ALL_OLD) is not None:
            # 3. create and send back response
            return response.get_response(Constants.SUCCESS, Constants.SUCCESS)
        raise Exception(response.get_custom_exception(Constants.NOT_FOUND, Constants.NOT_FOUND))
    raise Exception(response.get_custom_exception(Constants.BAD_REQUEST, Constants.INVALID_JSON_FORMAT))
