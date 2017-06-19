from imports.constants import Constants
from imports.response import Response
from imports.table import Table


def lambda_handler(event, context):
    group_name = event.get('group_name', "").strip()
    image_id = event.get('image_id', "").strip()
    group_id = event.get('group_id', "").strip()
    user_id = event.get('user_id', "").strip()

    response = Response()
    if user_id != "" and group_name != "" and image_id != "" and group_id != "":

        group_table = Table("group")
        if group_table.get_table_object() is None:
            raise Exception(response.get_custom_exception(code=Constants.SERVER_ERROR, message=Constants.SERVER_ERROR))

        key = {'group_id': group_id}
        group = group_table.get_item_by_key(key=key)
        if group is None:
            raise Exception(response.get_custom_exception(code=Constants.NOT_FOUND, message=Constants.NOT_FOUND))

        key = {'group_id': group_id}
        update_expression = 'SET group_name = :group_name, user_id = :user_id, image_id = :image_id'
        expression_attribute_values = {
            ':group_name': group_name,
            ':user_id': user_id,
            ':image_id': image_id
        }
        return_values = "ALL_NEW"

        result = group_table.update_item_by_key(
            key=key,
            update_expression=update_expression,
            expression_attribute_values=expression_attribute_values,
            return_values=return_values
        )
        if result is None:
            raise Exception(response.get_custom_exception(code=Constants.SERVER_ERROR, message=Constants.SERVER_ERROR))

        response_object = {'groupId': group_id}
        return response.get_response(Constants.SUCCESS, Constants.SUCCESS, response_object)
    raise Exception(response.get_custom_exception(Constants.BAD_REQUEST, Constants.INVALID_JSON_FORMAT))
