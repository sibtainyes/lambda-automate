from imports.models.scheduler import Scheduler
from imports.constants import Constants
from imports.response import Response
from imports.table import Table
from util.util import Util

"""
__author__      = Umair Ansari
__copyright__   = Copyright 2007, Cielo WiGle
__date__        = 10, May 2017
__version__     = 1.0.0
"""


def lambda_handler(event, context):

    mac_address = event.get('mac_address', "")
    schedule_id = event.get('schedule_id', "")
    last_updated_at = 0

    response = Response()
    if 'last_updated_at' in event:
        last_updated_at = int(event["last_updated_at"])

    if mac_address != "" and schedule_id != "":
        util = Util()

        utc_ts = int(util.get_current_time_utc())

        scheduler_table = Table(Scheduler.SCHEDULER_TABLE)
        key = {'mac_address': mac_address, 'schedule_id': (schedule_id)}
        scheduler = scheduler_table.get_item_by_key(key)

        if scheduler is not None:
            if scheduler["updated_at"] == int(last_updated_at):

                key = {'mac_address': mac_address, 'schedule_id': schedule_id}
                update_expression = "SET update_type = :update_type,  is_deleted = :one , updated_at = :date"
                expression_attribute_values = {
                    ':update_type': "SchDeleted",
                    ':one': 1,
                    ':date': utc_ts
                }
                return_values = "ALL_NEW"

                response_object = scheduler_table.update_item_by_key(key, update_expression,
                                                                     expression_attribute_values, return_values)
                return response.get_response(Constants.PRECONDITION_FAILED, Constants.PRECONDITION_FAILED,
                                             response_object)
            else:
                raise Exception(response.get_custom_exception(Constants.CONFLICT, Constants.CONFLICT))
        else:
            raise Exception(response.get_custom_exception(Constants.NOT_FOUND, Constants.NOT_FOUND))

    else:
        raise Exception(response.get_custom_exception(Constants.BAD_REQUEST, Constants.INVALID_JSON_FORMAT))

