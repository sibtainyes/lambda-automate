from imports.constants import Constants
from imports.models.devices import Devices
from imports.response import Response
from imports.table import Table
from util.util import Util


"""
__author__      = Umair Ansari
__copyright__   = Copyright 2007, Cielo WiGle
__date__        = 26, May 2017
__version__     = 1.0.0
"""


def lambda_handler(event, context):
    mac_address = event.get('mac_address', "")
    device_id = event.get('device_id', "")
    device_name = event.get('device_name', "")
    created_at = event.get('created_at', "")
    wifi_name = event.get('wifi_name', "")

    response = Response()
    if mac_address != "" and device_id != "" and device_name != "" and isinstance(created_at, int) and created_at != 0 and wifi_name != "":
        updated_at = Util().get_current_time_utc()
        devices_table = Table(Devices.DEVICES_TABLE)
        if devices_table.get_table_object() is None:
            raise Exception(response.get_custom_exception(code=Constants.SERVER_ERROR, message=Constants.SERVER_ERROR))

        key = {'mac_address': mac_address, 'created_at': created_at},
        condition_expression = "device_id = :deviceId",
        update_expression = "set update_type = :update_type, device_name = :deviceName, updated_at = :updated_at, wifi_name = :wifi_name",
        expression_attribute_values = {
            ':update_type': "deviceEdited",
            ':deviceId': device_id,
            ':deviceName': device_name,
            ':updated_at': updated_at,
            ':wifi_name': wifi_name
                                      },
        return_values = "UPDATED_NEW"
        result = devices_table.update_item_by_key(
            key=key,
            update_expression=update_expression,
            expression_attribute_values=expression_attribute_values,
            return_values=return_values,
            condition_expression=condition_expression
        )
        if result is None:
            raise Exception(response.get_custom_exception(code=Constants.NOT_FOUND, message=Constants.NOT_FOUND))
        return response.get_response(code=Constants.SUCCESS, message=Constants.SUCCESS)
    raise Exception(response.get_custom_exception(code=Constants.BAD_REQUEST, message=Constants.INVALID_JSON_FORMAT))
