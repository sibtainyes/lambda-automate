from imports.models.devices import Devices
from imports.constants import Constants
from imports.response import Response
from imports.table import Table
from util.util import Util

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
    device_coordinates = event['device_coordinates']
    mac_address = str(event['mac_address'])
    created_at = event['created_At']
    threshold = event['threshold']
    device_id = event['device_id']

    response = Response()

    if mac_address != "" and device_id != "" and threshold != "" and device_coordinates != "" and created_at != "":

        devices_table = Table(Devices.DEVICES_TABLE)
        if devices_table.get_table_object() is None:
            raise Exception(response.get_custom_exception(Constants.SERVER_ERROR, Constants.SERVER_ERROR))

        key = {'mac_address': mac_address, 'created_at': created_at}
        condition_expression = "device_id = :deviceId"
        update_expression = "set update_type = :update_type, device_coordinates = :device_coordinates, threshold = :threshold, updated_at = :updated_at"
        expression_attribute_values = {
            ':update_type': "deviceLocationEdited",
            ':deviceId': device_id,
            ':device_coordinates': device_coordinates,
            ':threshold': threshold,
            ':updated_at': Util().get_current_time_utc()}
        return_values = "UPDATED_NEW"

        result = devices_table.update_item_by_key(key, update_expression, expression_attribute_values, return_values, condition_expression)

        if result is None:
            raise Exception(response.get_custom_exception(Constants.SERVER_ERROR, Constants.SERVER_ERROR))
        return response.get_response(Constants.SUCCESS, Constants.SUCCESS)
    raise Exception(response.get_custom_exception(Constants.BAD_REQUEST, Constants.INVALID_JSON_FORMAT))
