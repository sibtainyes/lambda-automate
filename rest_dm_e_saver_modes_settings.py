from imports.models.devices import Devices
from imports.constants import Constants
from imports.response import Response
from imports.table import Table

"""
__author__      = Umair Ansari
__copyright__   = Copyright 2007, Cielo WiGle
__date__        = 10, May 2017
__version__     = 1.0.0
"""


def lambda_handler(event, context):
    """
    
    :param event: 
    :param context: 
    :return: 
    """
    mac_address = event['mac_address']
    created_at = event['device_created_at']

    response = Response()

    if created_at != "" and mac_address != "":
        devices_table = Table(Devices.DEVICES_TABLE)
        if devices_table.get_table_object() is None:
            raise Exception(response.get_custom_exception(Constants.SERVER_ERROR, Constants.SERVER_ERROR))

        key = {'mac_address': mac_address, 'created_at': created_at}
        devices_resp = devices_table.get_item_by_key(key)

        if devices_resp is not None:
            response_object = {
                "is_weather_enabled": devices_resp.get("is_weather_enabled", "0"),
                "is_intelli_mode_enabled": devices_resp.get("is_intelli_mode_enabled", "0")
            }

            return response.get_response(Constants.SUCCESS, Constants.SUCCESS, response_object)
        raise Exception(response.get_custom_exception(Constants.NOT_FOUND, Constants.NOT_FOUND))
    raise Exception(response.get_custom_exception(Constants.BAD_REQUEST, Constants.INVALID_JSON_FORMAT))
