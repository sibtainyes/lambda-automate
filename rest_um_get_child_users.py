from boto3.dynamodb.conditions import Key
from imports.models.user import User
from imports.constants import Constants
from imports.response import Response
from imports.table import Table

"""
__author__      = Umair Ansari
__copyright__   = Copyright 2007, Cielo WiGle
__date__        = 25, April 2017
__version__     = 1.0.0
"""


def lambda_handler(event, context):
    """
    
    :param event: 
    :param context: 
    :return: 
    """
    user_id = event.get(User.USER_ID, "").strip()
    response = Response()
    if user_id != "":
        user_table = Table(User.USER_TABLE)
        user = user_table.get_item_by_key({User.USER_ID: user_id})
        if user is None:
            raise Exception(response.get_custom_exception(Constants.NOT_FOUND, Constants.NOT_FOUND))
        ke = Key(User.PARENT_USER).eq(user_id) & Key(User.IS_DELETED).eq(0)
        user = user_table.get_item_via_query(ke, Constants.PARENT_USER_IS_DELETED)
        if user is None:
            raise Exception(response.get_custom_exception(Constants.NOT_FOUND, Constants.NOT_FOUND))

        child_users = []
        for list_users in user:
            child_users.append(
                {
                    User.CONTACT_NO: list_users[User.CONTACT_NO],
                    User.CREATED_AT: list_users[User.CREATED_AT],
                    User.EMAIL_ID: list_users[User.EMAIL_ID],
                    User.UPDATED_AT: list_users[User.UPDATED_AT],
                    User.USER_ID: list_users[User.USER_ID]
                }
            )
        return response.get_response(Constants.SUCCESS, Constants.SUCCESS, child_users)
    raise Exception(response.get_custom_exception(Constants.BAD_REQUEST, Constants.INVALID_JSON_FORMAT))


