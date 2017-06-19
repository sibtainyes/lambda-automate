from imports.constants import Constants
from imports.models.device_state import DeviceState
from imports.response import Response
from imports.table import Table


def lambda_handler(event, context):
    mac_address = str(event.get('mac_address', ""))
    filter_flag = event['filter_flag']

    response = Response()
    if mac_address != "" and isinstance(filter_flag, int):
        device_state_table = Table(table_name=DeviceState.DEVICE_STATE)
        key = {'mac_address': mac_address}
        response = device_state_table.get_item_by_key(key=key)
        if response is None:
            raise Exception(response.get_custom_exception(code=Constants.NOT_FOUND, message=Constants.NOT_FOUND))

        update_expression = 'SET device_filter_flag = :filter_flag, device_filter_duration = :filter_duration'
        expression_attribute_values = {
            ':filter_flag': filter_flag,
            ':filter_duration': 0
        }
        return_values = "UPDATED_NEW"

        result = device_state_table.update_item_by_key(
            key=key,
            update_expression=update_expression,
            expression_attribute_values=expression_attribute_values,
            return_values=return_values
        )
        if result is None:
            raise Exception(response.get_custom_exception(code=Constants.SERVER_ERROR, message=Constants.SERVER_ERROR))
        return response.get_response(code=Constants.SUCCESS, message=Constants.SUCCESS)
    raise Exception(response.get_custom_exception(code=Constants.BAD_REQUEST, message=Constants.INVALID_JSON_FORMAT))
