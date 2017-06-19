import json

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
    # from User Model
    user_id = event.get(User.USER_ID, "").strip()
    currency_symbol = event.get(User.CURRENCY_SYMBOL, "").strip()
    cur_sym_orientation = event.get(User.CURRENT_SYSTEM_ORIENTATION, "").strip()
    unit_price = event.get(User.UNIT_PRICE, "").strip()
    dev_currency_index = event.get(User.DEV_CURRENCY_INDEX, "").strip()

    is_default = Constants.DEFAULT_INT
    response = Response()

    if user_id != "" and currency_symbol != "" and unit_price != "" and cur_sym_orientation != "":
        user_table = Table(User.USER_TABLE)
        user = user_table.get_item_by_key({User.USER_ID: user_id})
        if user is not None:
            if User.CURRENCY_SYMBOL not in user or currency_symbol != user[User.CURRENCY_SYMBOL] or unit_price != user[User.UNIT_PRICE] or cur_sym_orientation != user[User.CURRENT_SYSTEM_ORIENTATION]:
                response = user_table.update_item_by_key(
                    {User.USER_ID: user_id},
                    "set currency_symbol = :currency_symbol, cur_sym_orientation = :cur_sym_orientation, unit_price = :unit_price, dev_currency_index = :dev_currency_index, is_default = :is_default",
                    {
                        ':currency_symbol': currency_symbol,
                        ':cur_sym_orientation': cur_sym_orientation,
                        ':unit_price': unit_price,
                        ':dev_currency_index': dev_currency_index,
                        ':is_default': is_default
                    },
                    "UPDATED_NEW")
                if response is not None:
                    return response.get_response(Constants.SUCCESS, Constants.SUCCESS)
                raise Exception(response.get_custom_exception(Constants.SERVER_ERROR, Constants.SERVER_ERROR))
            return response.get_response(Constants.SUCCESS, Constants.SUCCESS)
        raise Exception(response.get_custom_exception(Constants.NOT_FOUND, Constants.NOT_FOUND))
    raise Exception(response.get_custom_exception(Constants.BAD_REQUEST, Constants.INVALID_JSON_FORMAT))
