from boto3.dynamodb.conditions import Key, Attr
from imports.models.devices import Devices
from imports.constants import Constants
from imports.response import Response
from imports.table import Table


def lambda_handler(event, context):
    group_id = event.get('groupId', "").strip()

    response = Response()
    if group_id != "":

        group_table = Table("group")
        key = {
            'group_id': group_id
        }
        group = group_table.get_item_by_key(key=key)
        if group is None:
            raise Exception(response.get_custom_exception(Constants.NOT_FOUND, Constants.NOT_FOUND))

        # Check if any device belongs to a group
        user_id = group['user_id']
        is_registered = 1

        devices_table = Table(Devices.DEVICES_TABLE)
        index_name = 'user_id-is_registered-index',
        key_condition_expression = Key('user_id').eq(user_id) & Key('is_registered').eq(is_registered),
        filter_expression = Attr('group_id').eq(group_id)
        response = devices_table.get_item_via_query(
            key_expression=key_condition_expression,
            index=index_name,
            filter_expression=filter_expression
        )
        if response is not None:
            # Some device belongs to the group
            raise Exception(response.get_custom_exception(Constants.CONFLICT, Constants.CONFLICT))

        key = {
            'group_id': group_id
        }
        result = group_table.delete_item_by_key(key=key, return_values="ALL_OLD")
        if result is None:
            raise Exception(response.get_custom_exception(Constants.SERVER_ERROR, Constants.SERVER_ERROR))

        response_object = {'group_id': group_id}
        return response.get_response(Constants.SUCCESS, Constants.SUCCESS, response_object)
    raise Exception(response.get_custom_exception(Constants.BAD_REQUEST, Constants.INVALID_JSON_FORMAT))
