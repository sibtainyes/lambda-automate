"""
__author__      = Umair Ansari
__copyright__   = Copyright 2007, Cielo WiGle
__date__        = 26, May 2017
__version__     = 1.0.0
"""
from imports.constants import Constants
from imports.models.devices import Devices
from imports.response import Response
from imports.table import Table
from util.util import Util


def lambda_handler(event, context):
    mac_address = event.get('mac_address', "")
    created_at = event.get('created_at', "")

    response = Response()
    if mac_address != "" and isinstance(created_at, int) and created_at != 0:

        un_register_date = Util().get_current_time_utc()
        devices_table = Table(Devices.DEVICES_TABLE)
        if devices_table.get_table_object() is None:
            raise Exception(response.get_custom_exception(code=Constants.SERVER_ERROR, message=Constants.SERVER_ERROR))

        key = {'mac_address': mac_address, 'created_at': created_at},
        condition_expression = "is_registered = :one",
        update_expression = "SET update_type = :update_type, is_registered = :zero , unregistered_date = :date, updated_at = :date",
        expression_attribute_values = {
            ':update_type': "deviceUnregistered",
            ':one': 1,
            ':zero': 0,
            ':date': un_register_date
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
