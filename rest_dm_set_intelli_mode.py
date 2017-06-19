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
    is_intelli_enabled = str(event['is_intelli_enabled'])

    response = Response()
    if mac_address != "" and created_at != "" and is_intelli_enabled != "":

        devices_table = Table(Devices.DEVICES_TABLE)
        if devices_table.get_table_object() is None:
            raise Exception(response.get_custom_exception(Constants.SERVER_ERROR, Constants.SERVER_ERROR))

        key = {'mac_address': mac_address, 'created_at': created_at}
        devices_resp = devices_table.get_item_by_key(key)

        if devices_resp is not None:
            key = {'mac_address': mac_address, 'created_at': created_at}
            update_expression = "SET is_intelli_mode_enabled = :is_intelli_mode_enabled"
            expression_attribute_values = {':is_intelli_mode_enabled': int(is_intelli_enabled)}
            return_values = "UPDATED_NEW"

            result = devices_table.update_item_by_key(key, update_expression, expression_attribute_values, return_values)

            if result is not None:
                return response.get_response(Constants.SUCCESS, Constants.SUCCESS)
        raise Exception(response.get_custom_exception(Constants.NOT_FOUND, Constants.NOT_FOUND))
    raise Exception(response.get_custom_exception(Constants.BAD_REQUEST, Constants.INVALID_JSON_FORMAT))
