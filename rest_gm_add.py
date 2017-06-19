from imports.constants import Constants
from imports.response import Response
from imports.table import Table
import uuid


def lambda_handler(event, context):
    user_id = event.get('user_id', "").strip()
    group_name = event.get('group_name', "").strip()
    image_id = event.get('image_id', "").strip()

    response = Response()
    if user_id != "" and group_name != "" and image_id != "":

        group_id = str(uuid.uuid1())

        group_table = Table("group")
        if group_table.get_table_object() is None:
            raise Exception(response.get_custom_exception(Constants.SERVER_ERROR, Constants.SERVER_ERROR))

        item = {
            'group_id': group_id,
            'group_name': group_name,
            'image_id': image_id,
            'user_id': user_id
        }

        exception = group_table.put_item(item=item)
        if exception is not None:
            raise Exception(response.get_custom_exception(Constants.SERVER_ERROR, Constants.SERVER_ERROR))

        response_object = {'group_id': group_id}
        return response.get_response(Constants.SUCCESS, Constants.SUCCESS, response_object)
    raise Exception(response.get_custom_exception(Constants.BAD_REQUEST, Constants.INVALID_JSON_FORMAT))
