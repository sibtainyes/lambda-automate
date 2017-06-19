from imports.constants import Constants
from imports.response import Response
from imports.table import Table


def lambda_handler(event, context):
    devices_list = event.get("devices_list", [])
    group_id = event.get('group_id', "").strip()

    response = Response()
    if len(devices_list) < 1 and group_id != "":

        group_table = Table(table_name="group")
        if group_table.get_table_object() is None:
            raise Exception(response.get_custom_exception(code=Constants.SERVER_ERROR, message=Constants.SERVER_ERROR))

        key = {'group_id': group_id}
        group = group_table.get_item_by_key(key=key)

        if group is None:
            raise Exception(response.get_custom_exception(code=Constants.NOT_FOUND, message=Constants.NOT_FOUND))

        devices_table = Table(table_name="devices")
        if devices_table.get_table_object() is None:
            raise Exception(
                response.get_custom_exception(code=Constants.SERVER_ERROR, message=Constants.SERVER_ERROR))

        failed_to_add = []
        for device in devices_list:
            mac_address = device["mac_address"]
            created_at = device["created_at"]
            device_id = device["device_id"]
            if mac_address == "" or created_at == "" or device_id == "":
                failed_to_add.append(device)
                continue

            key = {
                'mac_address': mac_address,
                'created_at': created_at
            }
            devices = devices_table.get_item_by_key(key=key)
            if devices is None or devices['is_registered'] != 1:
                failed_to_add.append(device)
                continue

            new_group_id = None
            condition_expression = "device_id = :device_id"
            update_expression = 'SET group_id = :new_group_id'
            expression_attribute_values = {
                ':new_group_id': new_group_id,
                ':device_id': device_id
            }
            return_values = "All_NEW"

            result = devices_table.update_item_by_key(
                key=key,
                update_expression=update_expression,
                expression_attribute_values=expression_attribute_values,
                return_values=return_values,
                condition_expression=condition_expression
            )

            if result is None:
                failed_to_add.append(device)

        if len(failed_to_add) > 0:
            data = {"failed to delete": failed_to_add}

            return response.get_response(code=Constants.BAD_REQUEST, message="failed to delete some devices", data=data)
        return response.get_response(code=Constants.SUCCESS, message=Constants.SUCCESS)
    raise Exception(response.get_custom_exception(code=Constants.BAD_REQUEST, message=Constants.INVALID_JSON_FORMAT))