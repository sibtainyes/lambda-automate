from boto3.dynamodb.conditions import Key, Attr

from imports.models.scheduler import Scheduler
from imports.constants import Constants
from imports.response import Response
from imports.table import Table

"""
__author__      = Umair Ansari
__copyright__   = Copyright 2007, Cielo WiGle
__date__        = 10, May 2017
__version__     = 1.0.0
"""


def lambda_handler(event, context):

    device_created_at = int(event['device_created_at'])
    mac_address = event.get('mac_address', "")

    response = Response()
    if mac_address == '':
        raise Exception(response.get_custom_exception(Constants.BAD_REQUEST, Constants.INVALID_JSON_FORMAT))
    else:
        scheduler_table = Table(Scheduler.SCHEDULER_TABLE)

        ke = Key('mac_address').eq(mac_address)
        fe = Attr('is_deleted').eq(0) & Attr('device_created_at').eq(device_created_at);

        schedules = scheduler_table.get_item_via_query(ke, None, fe)

        if schedules is None:
            schedules = []

        schedules_list = []

        for schedule in schedules:
            schedule_object = get_schedule_object(schedule)
            schedules_list.append(schedule_object)
        response_object = {'list_of_schedules': schedules_list}
        return response.get_response(Constants.SUCCESS, Constants.SUCCESS, response_object)


def get_schedule_object(schedule):
    return {

        'appliance_object': schedule["appliance"],

        'device_id': schedule["device_id"],
        'device_created_at': str(schedule["device_created_at"]),

        'schedule_id': schedule["schedule_id"],
        'schedule_created_at': str(schedule["schedule_created_at"]),
        'actions': schedule["actions"],

        'user_id': schedule["user_id"],
        'last_updated_at': str(schedule["updated_at"]),

        'curr_app_time_zone': schedule["current_app_timezone"],
        'days': schedule["days"],
        'schedule_time': schedule["schedule_time"],
        'label': schedule["label"],
        'is_forwarded': str(schedule["is_forwarded"]),
        'is_executed': str(schedule["is_executed"]),
        'is_enabled': str(schedule["is_enabled"])
    }