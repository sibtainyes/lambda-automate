from imports.models.device_state import DeviceState
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
    setting_type = int(event['setting_type'])  # 1,2, 3
    setting_value = event.get('setting_value', "")
    mac_address = event.get('mac_address', "")

    response = Response()

    if isinstance(setting_type, int) and setting_value != "" and mac_address != "":

        device_state_table = Table(DeviceState.DEVICE_STATE)
        if device_state_table.get_table_object() is None:
            raise Exception(response.get_custom_exception(Constants.SERVER_ERROR, Constants.SERVER_ERROR))

        key = {'mac_address': mac_address}
        device_state = device_state_table.get_item_by_key(key)
        if device_state is not None:
            if device_state["device_type"] != "BREEZ":  # this function should call only for BREEZ device
                raise Exception(response.get_custom_exception(Constants.BAD_REQUEST, "Wrong Device"))

            device_settings = {}
            if 'device_settings' in device_state:
                device_settings = device_state["device_settings"]
            else:
                device_settings["transmitterValue"] = '1111'
                device_settings["brightnessValue"] = '1'
                device_settings["screenDisplayValue"] = '1'

            device_settings["transmitterValue"] = setting_value if setting_type == 1 else device_settings["transmitterValue"]
            device_settings["brightnessValue"] = setting_value if setting_type == 2 else device_settings["brightnessValue"]
            device_settings["screenDisplayValue"] = setting_value if setting_type == 3 else device_settings["screenDisplayValue"]

            expression_attribute_values = {':device_settings': device_settings, ':update_type': "deviceSettingsEdited"}
            update_expression = "SET device_settings = :device_settings, update_type = :update_type "
            key = {'mac_address': mac_address}
            result_values = "UPDATED_NEW"

            result = device_state_table.update_item_by_key(key, update_expression, expression_attribute_values, result_values)
            if result is None:
                raise Exception(response.get_custom_exception(Constants.SERVER_ERROR, Constants.SERVER_ERROR))
            return response.get_response(Constants.SUCCESS, Constants.SUCCESS)
        else:
            raise Exception(response.get_custom_exception(Constants.NOT_FOUND, Constants.NOT_FOUND))
    raise Exception(response.get_custom_exception(Constants.BAD_REQUEST, Constants.INVALID_JSON_FORMAT))
