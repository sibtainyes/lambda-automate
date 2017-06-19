from boto3.dynamodb.conditions import Key
from datetime import datetime

from imports.models.appliance_codes import ApplianceCodes
from imports.models.appliance_rules import ApplianceRules
from imports.models.device_state import DeviceState
from imports.models.appliance import Appliance
from imports.models.actions import Actions
from imports.models.devices import Devices
from imports.constants import Constants
from imports.response import Response
from imports.table import Table
from util.util import Util


response = Response()

"""
__author__      = Umair Ansari
__copyright__   = Copyright 2007, Cielo WiGle
__date__        = 10, May 2017
__version__     = 1.0.0
"""


def lambda_handler(event, context):
    """
    
    :param event: 
    :param context: 
    :return: 
    """

    device_id = event.get('device_id', "").strip()
    mac_address = event.get('mac_address', "").strip()
    appliance_id = event.get('appliance_id', "").strip()
    created_at = event.get('created_at', "").strip()
    codes_required = event.get('codesRequired', 0)

    if device_id != "" and appliance_id['applianceId'] != "" and appliance_id['applianceType'] != "" and created_at != "":
        util = Util()
        updated_at = util.get_current_time_utc()

        device_state_table = Table(DeviceState.DEVICE_STATE)
        if device_state_table.get_table_object() is None:
            raise Exception(response.get_custom_exception(Constants.SERVER_ERROR, Constants.SERVER_ERROR))

        key = {'mac_address': mac_address}
        device = device_state_table.get_item_by_key(key)

        is_faren = 0
        device_time_zone = device["device_time_zone"]

        # Parental_Control
        # Calculate hours, minutes and offset from device timezone
        device_time_zone_offset = device_time_zone[0]
        device_time_zone_time = device_time_zone[1:].split(':')
        device_time_zone_hour = int(device_time_zone_time[0])
        device_time_zone_minute = int(device_time_zone_time[1])

        default_power_on_start_utc = util.convert_to_utc(Constants.DEFAULT_POWER_ON_START, device_time_zone_offset,
                                                    device_time_zone_hour, device_time_zone_minute)
        default_power_on_end_utc = util.convert_to_utc(Constants.DEFAULT_POWER_ON_END, device_time_zone_offset,
                                                  device_time_zone_hour, device_time_zone_minute)
        default_power_off_start_utc = util.convert_to_utc(Constants.DEFAULT_POWER_OFF_START, device_time_zone_offset,
                                                     device_time_zone_hour, device_time_zone_minute)
        default_power_off_end_utc = util.convert_to_utc(Constants.DEFAULT_POWER_OFF_END, device_time_zone_offset,
                                                   device_time_zone_hour, device_time_zone_minute)

        # For parental control
        power_on = {
            "start_time": default_power_on_start_utc,
            "end_time": default_power_on_end_utc,
            "is_enabled": 0,
        }
        power_off = {
            "start_time": default_power_off_start_utc,
            "end_time": default_power_off_end_utc,
            "is_enabled": 0,
        }

        appliance_table = Table(Appliance.APPLIANCE_TABLE)
        key = {'appliance_id': int(appliance_id['applianceId'])}
        appliance_resp = appliance_table.get_item_by_key(key)

        fan_speed = "high"
        if appliance_resp is not None:
            if 'is_faren' in appliance_resp:
                is_faren = appliance_resp["is_faren"]
            appliance = appliance_resp
            swing = appliance["swing"].split(':')[0]
        else:
            raise Exception(response.get_custom_exception(Constants.NOT_FOUND, Constants.NOT_FOUND))

        temp = "78" if is_faren == 1 else "26"

        latest_action = device['latest_action']
        latest_action['power'] = 'off'
        latest_action['temp'] = temp
        latest_action['swing'] = swing
        latest_action['fanspeed'] = fan_speed
        latest_action['mode'] = "cool"
        latest_action['ontimestamp'] = updated_at
        latest_action['fanspeed'] = fan_speed

        power_on_actions = {
            "power": "on",
            "temp": temp,
            "mode": "cool"
        }
        power_on.update({"actions": power_on_actions})
        parental_control = {
            "power_on": power_on,
            "power_off": power_off
        }
        appliance_id = [appliance_id]
        latest_action['timestamp'] = updated_at
        dev_status = int(device['device_status'])
        if dev_status == 0:
            dev_status = 'off'
            latest_action['statustimestamp'] = updated_at
        elif dev_status == 1:
            dev_status = 'on'

        lastStatDetails = {
            "LastActions": {
                "DeviceStatus": dev_status,
                "power": "off",
                "temp": int(temp)
            },
            "stat_timestamp": "0"
        }

        app_id = str(appliance_id[0]['applianceId'])
        new_device_id = util.id_generator(6)
        device_state_response = update_device_state(appliance_id, device_id, device_state_table, lastStatDetails, latest_action, mac_address,
                            new_device_id, parental_control, updated_at)

        if device_state_response is None:
            raise Exception(response.get_custom_exception(Constants.SERVER_ERROR, Constants.SERVER_ERROR))

        device_response = update_device(created_at, device_id, mac_address, updated_at)
        if device_response is None:
            raise Exception(response.get_custom_exception(Constants.NOT_FOUND, Constants.NOT_FOUND))

        save_device_response = save_device(appliance_id, device_response, new_device_id, updated_at)
        if save_device_response is None:
            raise Exception(response.get_custom_exception(Constants.SERVER_ERROR, Constants.SERVER_ERROR))

        save_action("Cloud", 1, updated_at, "ApplianceChanged", appliance['name'] + '-' + appliance['model_number'],
                    app_id, "0,0", "N/A", "N/A", "Cloud", device_response['device_coordinates'], created_at, new_device_id, 0,
                    device_response['user_id'])
        save_action("Cloud", 1, updated_at + 1, "DeviceStatus", dev_status, app_id, "0,0", "N/A", "N/A", "Cloud",
                    device_response['device_coordinates'], created_at, new_device_id, 0, device_response['user_id'])

        response_object = {'deviceId': new_device_id,
                          'createdAt': str(updated_at)
                          }

        # Check if codes are required
        if codes_required:
            appliance_id = int(event['applianceId']['applianceId'])
            appliance_codes_list = get_appliance_codes(appliance_id)
            appliance_rules_list = get_appliance_rules(appliance_id)
            response_object.update({
                'listOfApplianceCodes': appliance_codes_list,
                'listOfApplianceRules': appliance_rules_list
            })
        return response.get_response(Constants.SUCCESS, Constants.SUCCESS, response_object)
    raise Exception(response.get_custom_exception(Constants.BAD_REQUEST, Constants.INVALID_JSON_FORMAT))


def update_device_state(appliance_id, device_id, device_state_table, lastStatDetails, latest_action, mac_address,
                        new_device_id, parental_control, updated_at):
    key = {'mac_address': mac_address},
    condition_expression = "device_id = :deviceId",
    update_expression = "set device_id = :new_device_id, appliance_id = :appliance_id, updated_at = :updated_at,parental_control = :parental_control, last_stat_details = :last_stat_details, latest_action = :latest_action, device_created_at = :updated_at, device_filter_duration = :filter_duration, device_filter_flag = :filter_flag",
    expression_attribute_values = {
                                      ':deviceId': device_id,
                                      ':new_device_id': new_device_id,
                                      ':appliance_id': appliance_id,
                                      ':updated_at': updated_at,
                                      ':parental_control': parental_control,
                                      ':last_stat_details': lastStatDetails,
                                      ':latest_action': latest_action,
                                      ':filter_duration': 0,
                                      ':filter_flag': 1
                                  },
    return_values = "NONE"
    return device_state_table.update_item_by_key(key, update_expression, expression_attribute_values, return_values,
                                          condition_expression)


def update_device(created_at, device_id, mac_address, updated_at):
    devices_table = Table(Devices.DEVICES_TABLE)
    if devices_table is None:
        return None

    key = {'mac_address': mac_address, 'created_at': int(created_at)},
    condition_expression = "device_id = :deviceId",
    update_expression = "set is_registered = :is_registered, update_type = :update_type, updated_at = :updated_at",
    expression_attribute_values = {
        ':is_registered': 0,
        ':update_type': "deviceApplianceChanged",
        ':deviceId': device_id,
        ':updated_at': updated_at
    },
    return_values = "ALL_OLD"
    return devices_table.update_item_by_key(key, update_expression, expression_attribute_values, return_values,
                                              condition_expression)


def save_device(appliance_id, device, new_device_id, updated_at):
    devices_table = Table(Devices.DEVICES_TABLE)
    if devices_table is None:
        return None
    devices_table.put_item(
        {
            'appliance_id': appliance_id,
            'application_type': device["application_type"],
            'application_version': device["application_version"],
            'broadcast_name': device["broadcast_name"],
            'device_id': new_device_id,
            'device_name': device["device_name"],
            'device_time_zone': device["device_time_zone"],
            'mac_address': device["mac_address"],
            'user_id': device["user_id"],
            'created_at': int(updated_at),
            'updated_at': updated_at,
            'device_coordinates': device["device_coordinates"],
            'device_type': device["device_type"],
            'device_type_version': device["device_type_version"],
            'fw_version': device["fw_version"],
            'is_energy_device': device["is_energy_device"],
            'is_registered': 1,
            'wifi_name': device["wifi_name"],
            'is_blocked': device["is_blocked"],
            'block_message': device["block_message"],
            'update_type': "NewApplianceRecord",
            'group_id': device.get('group_id', None)
        }
    )
    return True


def get_appliance_codes(appliance_id):
    appliance_code_table = Table(ApplianceCodes.APPLIANCE_CODE_TABLE)
    key = Key(ApplianceCodes.APPLIANCE_ID).eq(appliance_id)
    index = ApplianceCodes.APPLIANCE_ID_INDEX
    appliance_code = appliance_code_table.get_item_via_query(key, index)
    codes_list = []

    if appliance_code is not None:
        for code in appliance_code:
            code_object = {
                ApplianceCodes.VALUE: code[ApplianceCodes.VALUE],
                ApplianceCodes.CODE: code[ApplianceCodes.CODE],
                ApplianceCodes.MANUFACTURE_ID: code[ApplianceCodes.MANUFACTURE_ID],
                ApplianceCodes.APPLIANCE_ID: code[ApplianceCodes.APPLIANCE_ID],
                ApplianceCodes.TYPE: code[ApplianceCodes.TYPE],
                ApplianceCodes.IS_BASESTRING: code[ApplianceCodes.IS_BASESTRING],
                ApplianceCodes.IS_RULE_BASED: code[ApplianceCodes.IS_RULE_BASED],
                ApplianceCodes.CZ1: code.get(ApplianceCodes.CZ1, None),
                ApplianceCodes.CZ2: code.get(ApplianceCodes.CZ2, None),
                ApplianceCodes.CZ3: code.get(ApplianceCodes.CZ3, None),
                ApplianceCodes.CONSTRUCTED_BASE_STRING : code.get(ApplianceCodes.CONSTRUCTED_BASE_STRING, None),
                ApplianceCodes.RULE: code.get(ApplianceCodes.RULE, None)
            }
            codes_list.append(code_object)
    return codes_list


def get_appliance_rules(appliance_id):
    appliance_rules_table = Table(ApplianceRules.APPLIANCE_RULES_TABLE)
    rules_list = []

    key = Key(ApplianceRules.APPLIANCE_ID).eq(appliance_id)
    index = ApplianceRules.APPLIANCE_ID_INDEX
    appliance_rules = appliance_rules_table.get_item_via_query_count(key, index)

    if appliance_rules is not None:
        for rule in appliance_rules:
            rule_object = {
                ApplianceRules.MANUFACTURE_ID: rule[ApplianceRules.MANUFACTURE_ID],
                ApplianceRules.APPLIANCE_ID: rule[ApplianceRules.APPLIANCE_ID],
                ApplianceRules.MODE: rule[ApplianceRules.MODE],
                ApplianceRules.UI_RULES: rule[ApplianceRules.UI_RULES],
                ApplianceRules.EXTRA_AC_BUTTON: rule[ApplianceRules.EXTRA_AC_BUTTON],
                ApplianceRules.MODEL_RULES: rule[ApplianceRules.MODEL_RULES]
            }
            rules_list.append(rule_object)
    return rules_list


def save_action(action_source, is_performed, timestamp, action_type, description, appliance_id, application_coordinates,
                mobile_device_id, application_version, communication_source, device_coordinates, device_created_at,
                device_id, online_action_timestamp, user_id):

    actions_table = Table(Actions.ACTIONS_TABLE)
    actions_table.put_item(
        {
            "action_source": action_source,
            "is_performed": is_performed,
            "action_timestamp": int(timestamp),
            "action_date": str(datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')),
            "action_type": action_type,
            "action_value": description,
            "appliance_id": appliance_id,
            "application_coordinates": application_coordinates,
            "mobile_device_id": mobile_device_id,
            "application_version": application_version,
            "communication_source": communication_source,
            "device_coordinates": device_coordinates,
            "device_created_at": device_created_at,
            "device_id": device_id,
            "online_action_timestamp": int(online_action_timestamp),
            "user_id": user_id
        }
    )
