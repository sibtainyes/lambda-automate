from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime

from imports.models.schedule_notifications import ScheduleNotifications
from imports.models.appliance_codes import ApplianceCodes
from imports.models.appliance_rules import ApplianceRules
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
    response = Response()
    util = Util()

    application_version = event.get('application_version', "")
    curr_app_time_zone = event.get('curr_app_time_zone', "")
    mobile_device_id = event.get('mobile_device_id', "")
    application_type = event.get('application_type', "")
    appliance_object = event.get('appliance_object', "")
    action_string = event.get('action_string', "")
    schedule_time = event.get('schedule_time', "")
    mac_address = event.get('mac_address', "")
    schedule_id = event.get('schedule_id', "")
    device_id = event.get('device_id', "")
    actions = event.get('actions', "")

    last_updated_at = 0

    if 'last_updated_at' in event:
        last_updated_at = int(event["last_updated_at"])

    if 'dps' in event:
        dps = event['dps']
    else:
        notification_dps = actions["power"]
        dps = '1' if notification_dps == 'on' else '0'

    cs0 = '0'
    cs1 = '0'
    if 'CS0' in event and 'CS1' in event:
        cs0 = event['CS0']
        cs1 = event['CS1']

    if curr_app_time_zone == 'Asia/Karachi':
        curr_app_time_zone = "+5:00"
    elif curr_app_time_zone == 'Asia/Dubai':
        curr_app_time_zone = '+4:00'
    elif curr_app_time_zone == 'US/Pacific':
        curr_app_time_zone = '-7:00'
    elif curr_app_time_zone == "Asia/Riyadh":
        curr_app_time_zone = '+3:00'

    days = event['days']
    label = event['label']
    is_enabled = 1

    if label == '' or days == '' or curr_app_time_zone == '' or action_string == '' or mobile_device_id == '' or schedule_time == '' or mac_address == '' or device_id == '' or actions == '' or application_version == '' or application_type == '':
        raise Exception(response.get_custom_exception(Constants.BAD_REQUEST, Constants.INVALID_JSON_FORMAT))
    else:

        utc_ts = int(util.get_current_time_utc())
        scheduler_table = Table(Scheduler.SCHEDULER_TABLE)
        key = {'mac_address': mac_address, 'schedule_id': schedule_id}
        response = scheduler_table.get_item_by_key(key)

        if response is not None:

            if response["updated_at"] == int(last_updated_at) or last_updated_at == 0:

                is_schedule_available = is_schedule_on_time_available(schedule_time, days, mac_address, utc_ts, schedule_id)

                if is_schedule_available:
                    mode_rules, ui_rules = get_mode_rules(appliance_object["applianceId"], actions["mode"])
                    actions["moderules"] = mode_rules
                    actions["uirules"] = ui_rules

                    scheduler_table = Table(Scheduler.SCHEDULER_TABLE)
                    key = {'mac_address': mac_address, 'schedule_id': schedule_id}
                    update_expression = "SET dps = :dps, cs0 = :cs0, cs1 = :cs1, update_type = :update_type, mobile_device_id = :mobile_device_id, is_enabled = :isEnabled , updated_at = :date, application_type = :applicationType,current_app_timezone = :currapptz, application_version = :applicationVersion, actionString = :actionString, actions = :actions, days = :days, label = :label, schedule_time = :scheduleTime"
                    expression_attribute_values = {
                        ':dps': str(dps),
                        ':cs0': str(cs0),
                        ':cs1': str(cs1),
                        ':actionString': action_string,
                        ':update_type': "SchEdited",
                        ':mobile_device_id': mobile_device_id,
                        ':isEnabled': is_enabled,
                        ':date': utc_ts,
                        ':applicationType': application_type,
                        ':currapptz': curr_app_time_zone,
                        ':applicationVersion': application_version,
                        ':actions': actions,
                        ':days': days,
                        ':label': label,
                        ':scheduleTime': schedule_time
                    }
                    return_values = "UPDATED_NEW"
                    scheduler_table.update_item_by_key(key, update_expression, expression_attribute_values, return_values)

                    response_object = {'last_updated_at': str(utc_ts)}
                    return response.get_response(Constants.PRECONDITION_FAILED, Constants.PRECONDITION_FAILED, response_object)

                else:
                    raise Exception(response.get_custom_exception(Constants.SERVER_ERROR, Constants.SERVER_ERROR))
            else:
                raise Exception(response.get_custom_exception(Constants.CONFLICT, Constants.CONFLICT))
        else:
            raise Exception(response.get_custom_exception(Constants.NOT_FOUND, Constants.NOT_FOUND))


def get_mode_rules(appliance_id, mode):
    ui_rules = "default:default:default"
    mode_rules = "default:default:default".split(':')

    rules_table = Table(ApplianceRules.APPLIANCE_RULES_TABLE)
    key_condition_expression = Key('appliance_id').eq(int(appliance_id))
    filter_expression = Attr('mode').eq(mode)
    index_name = "appliance_id-index"
    rules_list = rules_table.get_item_via_query_count(key_condition_expression, index_name, filter_expression)
    if rules_list is not None:
        rules_list = rules_list[0]
        ui_rules = rules_list['ui_rules']
        mode_rules = rules_list['model_rules']
        mode_rules = mode_rules.split(':')

        codes_table = Table(ApplianceCodes)
        key_condition_expression = Key('appliance_id').eq(int(appliance_id))
        index_name = "appliance_id-index"

        codes_list = codes_table.get_item_via_query(key_condition_expression, index_name)
        if codes_list is not None:
            if mode_rules[0] != "default":
                codes_list = filter(lambda code: code['code'] == mode_rules[0] and "temp" in code['type'], codes_list)
                if len(codes_list) > 0:
                    code_type = codes_list[0]["type"]
                    code_value = codes_list[0]["value"].split(',')
                    if code_type == "powerwtempwmodewfanwswing" or code_type == "powerwtempwmodewfan":
                        mode_rules[0] = code_value[1]
                    else:
                        mode_rules[0] = code_value[0]
                else:
                    mode_rules[0] = "default"
            if mode_rules[1] != "default":
                codes_list = filter(lambda code: code['code'] == mode_rules[1] and "swing" in code['type'], codes_list)
                if len(codes_list) > 0:
                    code_type = codes_list[0]["type"]
                    code_value = codes_list[0]["value"].split(',')
                    if code_type == "powerwtempwmodewfanwswing":
                        mode_rules[1] = code_value[4]
                    else:
                        mode_rules[1] = code_value[0]
                else:
                    mode_rules[1] = "default"
            if mode_rules[2] != "default":
                codes_list = filter(lambda code: code['code'] == mode_rules[2] and "fan" in code['type'], codes_list)
                if len(codes_list) > 0:
                    code_type = codes_list[0]["type"]
                    code_value = codes_list[0]["value"].split(',')
                    if code_type == "powerwtempwmodewfanwswing" or code_type == "powerwtempwmodewfan":
                        mode_rules[2] = code_value[3]
                    elif code_type == "tempwmodewfan":
                        mode_rules[2] = code_value[2]
                    elif code_type == "modewfan":
                        mode_rules[2] = code_value[1]
                    else:
                        mode_rules[2] = code_value[0]
                else:
                    mode_rules[2] = "default"

    return ':'.join(mode_rules), ui_rules


def is_schedule_on_time_available(schedule_time, new_day_string, mac_address, new_sch_created_at):
    new_day_string = new_day_string.replace(',', '')
    scheduler_table = Table(Scheduler.SCHEDULER_TABLE)
    ke = Key('mac_address').eq(mac_address)
    fe = Attr('is_deleted').eq(0) & Attr('schedule_time').eq(schedule_time)
    index_name = "mac_address-schedule_time-indexFixed"
    schedule_list_arr = scheduler_table.get_item_via_query(ke, index_name, fe)

    utc_dt = datetime.utcnow()

    new_sch_created_date = datetime.fromtimestamp(int(new_sch_created_at))

    current_day_index = utc_dt.weekday()
    no_repeat_day_string = '0000000'
    if new_day_string == no_repeat_day_string:

        current_day_sch = filter(lambda sch: sch['days'] == '0,0,0,0,0,0,0', schedule_list_arr)
        if len(current_day_sch) > 0:

            for sch in current_day_sch:
                existing_sch_day = sch['days'].replace(',', '')
                if existing_sch_day == no_repeat_day_string:
                    # get notification from schedule notifications table and match the sch date time from that recod
                    result = check_no_repeat_schedule(True, sch, new_sch_created_date, schedule_time, new_day_string)
                    if not result:
                        return False
            return True
        else:
            current_day_sch = filter(lambda sch: (sch['days'].replace(',', '')[current_day_index] == '1'),
                                   schedule_list_arr)
            return False if len(current_day_sch) > 0 else True
    else:
        for sch in schedule_list_arr:
            existing_sch_day = sch['days'].replace(',', '')
            if existing_sch_day == no_repeat_day_string:
                # get notification from schedule notifications table and match the sch date time from that recod
                result = check_no_repeat_schedule(False, sch, new_sch_created_date, schedule_time, new_day_string)
                if not result:
                    return False
            else:
                result = str(''.join(chr(ord(_a) & ord(_b)) for _a, _b in zip(new_day_string, existing_sch_day)))
                if result != no_repeat_day_string:
                    return False
        return True


def check_no_repeat_schedule(is_no_repeat_string, schedule, new_sch_created_date, schedule_time, new_day_string):
    no_repeat_day_string = '0000000'
    key = Key('schedule_id').eq(schedule['schedule_id'])
    schedule_notification_table = Table(ScheduleNotifications.SCHEDULE_NOTIFICATION_TABLE)
    schedule_notification_list = schedule_notification_table.get_item_via_query(key)

    if schedule_notification_list is not None:
        schedule_notification = schedule_notification_list[0]  # May 12, 2016, 13:37
        date = datetime.strptime(schedule_notification['notification_date'], "%b %d, %Y, %H:%M")

        schedule_notification_day_index = int(date.weekday())
        temp_schedule_day_string = schedule_notification['days'].replace(',', '')

        temp_schedule_day_string = list(temp_schedule_day_string)
        temp_schedule_day_string[schedule_notification_day_index] = '1'
        temp_schedule_day_string = "".join(temp_schedule_day_string)

        if is_no_repeat_string:
            new_day_string = get_new_schedule_notification_string(new_sch_created_date, schedule_time, new_day_string)
        result = str(''.join(chr(ord(_a) & ord(_b)) for _a, _b in zip(new_day_string, temp_schedule_day_string)))
        if result != no_repeat_day_string:
            return False
    return True


def get_new_schedule_notification_string(new_schedule_created_date, schedule_time, new_day_string):
    schedule_time = schedule_time.split(':')
    schedule_hour = int(schedule_time[0])
    schedule_min = int(schedule_time[1])
    new_sch_date = datetime(new_schedule_created_date.year, new_schedule_created_date.month,
                            new_schedule_created_date.day, schedule_hour,
                            schedule_min, 0)
    new_sch_day_number = (new_sch_date.weekday())
    if new_sch_date < new_schedule_created_date:
        new_sch_day_number = (new_sch_date.weekday()) + 1
    new_day_string = list(new_day_string)
    new_day_string[new_sch_day_number] = '1'
    new_day_string = "".join(new_day_string)
    return new_day_string
