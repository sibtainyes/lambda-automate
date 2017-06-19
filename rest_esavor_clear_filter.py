import time
from imports.constants import Constants
from imports.models.device_state import DeviceState
from imports.response import Response
from imports.table import Table


def lambda_handler(event, context):
    mac_address = event.get('macAddress', '')
    device_id = event.get('deviceId', '')

    response = Response()
    if mac_address != "" and device_id != "":

        new_filter_duration = 0
        utc_timestamp_seconds = int(time.time())

        device_state_table = Table(table_name=DeviceState.DEVICE_STATE)
        key = {'mac_address': mac_address}
        response = device_state_table.get_item_by_key(key=key)
        if response is None:
            raise Exception(response.get_custom_exception(code=Constants.NOT_FOUND, message=Constants.NOT_FOUND))

        update_expression = 'SET device_filter_duration = :filter_duration'
        expression_attribute_values = {
            ':filter_duration': new_filter_duration
        }
        return_values = 'UPDATED_OLD'

        result = device_state_table.update_item_by_key(
            key=key,
            update_expression=update_expression,
            expression_attribute_values=expression_attribute_values,
            return_values=return_values
        )
        if result is None:
            raise Exception(response.get_custom_exception(code=Constants.NOT_FOUND, message=Constants.NOT_FOUND))

        old_filter_duration = result['Attributes']['device_filter_duration']

        ac_filter_history_table = Table('ac_filter_history')
        item = {
            'device_id': device_id,
            'filter_timestamp': utc_timestamp_seconds,
            'mac_address': mac_address,
            'filter_duration': old_filter_duration
        }
        exception = ac_filter_history_table.put_item(item=item)
        if exception is not None:
            raise Exception(response.get_custom_exception(code=Constants.SERVER_ERROR, message=Constants.SERVER_ERROR))

        return response.get_response(code=Constants.SUCCESS, message=Constants.SUCCESS)
    raise Exception(response.get_custom_exception(code=Constants.BAD_REQUEST, message=Constants.INVALID_JSON_FORMAT))
