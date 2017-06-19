from boto3.dynamodb.conditions import Key
from decimal import Decimal

from imports.models.central_system import CentralSystem
from imports.models.device_state import DeviceState
from imports.models.devices import Devices
from imports.models.things import Things
from imports.models.group import Group
from imports.constants import Constants
from imports.defaults import Defaults
from imports.response import Response
from imports.table import Table


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
    user_id = event.get('user_id', "")

    response = Response()
    central_sys_item = Defaults.CENTRAL_SYSTEM[Constants.ENVIRONMENT]
    if user_id != "":
        device_state_table = Table(DeviceState.DEVICE_STATE)
        devices_table = Table(Devices.DEVICES_TABLE)
        things_table = Table(Things.THINGS_TABLE)

        if device_state_table.get_table_object() is None or devices_table.get_table_object() is None or things_table.get_table_object() is None:
            raise Exception(response.get_custom_exception(Constants.SERVER_ERROR, Constants.SERVER_ERROR))

        key_condition_expression = Key('user_id').eq(user_id) & Key('is_registered').eq(1)
        index = "user_id-is_registered-index"
        device_list = devices_table.get_item_via_query(key_condition_expression, index)

        key_condition_expression = Key('user_id').eq(user_id)
        index = "user_id-index"
        device_state_list = device_state_table.get_item_via_query(key_condition_expression, index)

        devices_lst = []

        # Get list of groups for user
        groups_list = get_group_list(user_id)

        if device_list is not None:
            for device in device_list:
                for device_state in device_state_list:
                    if device_state["device_id"] == device["device_id"]:

                        thing_arn = Constants.DEFAULT_STRING
                        certificate_id = Constants.DEFAULT_STRING
                        certificate_arn = Constants.DEFAULT_STRING
                        certificate_pem = Constants.DEFAULT_STRING
                        key_pair = Constants.DEFAULT_STRING
                        if 'thing_arn' in device_state:
                            key = {
                                'thing_macaddress': device["mac_address"],
                                'thing_arn': device_state["thing_arn"]
                            }

                            thing = things_table.get_item_by_key(key)
                            if thing is not None and thing["device_id"] == device["device_id"]:
                                thing_arn = thing["thing_arn"]
                                certificate_id = thing["certificate_id"]
                                certificate_arn = thing["certificate_arn"]
                                certificate_pem = thing["certificate_pem"]
                                key_pair = thing["key_pair"]

                        if device["device_type"] == "wigle" or device["device_type"] == "BREEZ" or device["device_type"] == "BREEZ-I":
                            if "lat_env_var" in device_state:
                                lat_env = device_state["lat_env_var"]
                            else:
                                lat_env = {"temp": "0", "humidity": "0"}
                            usageToday = "N/A"
                            usage_timestamp = "N/A"
                            costToday = "N/A"
                            avgDaily = "N/A"
                            estMonthly = "N/A"
                        elif device["device_type"] == "ECONI":
                            if "lat_env_var" in device_state:
                                lat_env = device_state["lat_env_var"]
                            else:
                                lat_env = {"instantaneous_current": "0", "total_units": "0.0"}
                            usageToday = device_state["usage_today"]
                            usage_timestamp = device_state["usage_timestamp"]
                            costToday = device_state["cost_today"]
                            avgDaily = "0hr 0min"
                            estMonthly = "0.0"
                        elif device["device_type"] == "LUMI":
                            if "lat_env_var" in device_state:
                                lat_env = device_state["lat_env_var"]
                            else:
                                lat_env = {"instantaneous_current": "0", "total_units": "0.0"}
                            usageToday = device_state["usage_today"]
                            usage_timestamp = device_state["usage_timestamp"]
                            costToday = device_state["cost_today"]
                            avgDaily = "0hr 0min"
                            estMonthly = "0.0"
                        else:
                            lat_env = {}

                        instCurr = str(Decimal(0.00))
                        if "instantaneous_current" in device_state['lat_env_var']:
                            instCurr = str(device_state['lat_env_var']["instantaneous_current"])

                        total_units = str(Decimal(0.00))
                        if "total_units" in device_state['lat_env_var']:
                            total_units = str(device_state['lat_env_var']["total_units"])

                        latEnvVar = lat_env
                        device_settings = {}
                        if 'device_settings' in device_state:
                            device_settings = device_state["device_settings"]

                        # Make parental control object
                        parental_control_object = get_parental_control_object(device_state)

                        # Get group_id if exists else send None(null)
                        group_id = device.get('group_id', None)

                        # Get custom device image
                        device_image_url = device_state.get('device_image_url', None)

                        # AC filter
                        device_filter_duration = device_state.get('device_filter_duration', 0)
                        # Convert filter duration from seconds to hours
                        device_filter_duration = round(device_filter_duration / 3600, 2)
                        device_filter_flag = device_state.get('device_filter_flag', 1)

                        device_object = create_response_object(
                            device["device_id"],
                            device["device_name"],
                            device["device_type"],
                            device["device_type_version"],
                            device["broadcast_name"],
                            device["application_type"],
                            device["application_version"],
                            device["fw_version"],
                            device["device_time_zone"],
                            device["appliance_id"],
                            device["device_coordinates"],
                            device_state["device_status"],
                            device["is_energy_device"],
                            device_state["latest_action"],
                            device["mac_address"],
                            str(total_units),
                            device_state["wifi_name"],
                            user_id,
                            instCurr,
                            usageToday,
                            usage_timestamp,
                            costToday,
                            avgDaily,
                            estMonthly,
                            latEnvVar,
                            thing_arn,
                            certificate_id,
                            certificate_arn,
                            certificate_pem,
                            key_pair,
                            device["created_at"],
                            "N/A",
                            device['is_blocked'],
                            device['block_message'],
                            device_settings,
                            parental_control_object,
                            group_id,
                            device_image_url,
                            device_filter_duration,
                            device_filter_flag
                        )

                        devices_lst.append(device_object)
        response_object = {
            'ios_version': central_sys_item[CentralSystem.IOS_VERSION],
            'android_version': central_sys_item[CentralSystem.ANDROID_VERSION],
            'list_devices': devices_lst,
            'list_groups': groups_list,
        }
        return response.get_response(Constants.SUCCESS, Constants.SUCCESS, response_object)
    raise Exception(response.get_custom_exception(Constants.BAD_REQUEST, Constants.INVALID_JSON_FORMAT))


def get_group_list(user_id):
    groups_list = []
    group_table = Table(Group.GROUP_TABLE)
    key_condition_expression = Key('user_id').eq(user_id)
    groups = group_table.get_item_via_query(key_condition_expression, Group.USER_ID_INDEX)
    if groups is not None:
        for group in groups:
            groups_list.append({
                'group_id': group.get('group_id', None),
                'group_name': group.get('group_name', None),
                'user_id': group.get('user_id', None),
                'image_id': group.get('image_id', None)
            })
    return groups_list


def get_parental_control_object(device_state_object):
    parental_control_object = {}

    parental_control = device_state_object.get('parental_control', {})

    if parental_control:
        appliance_type = device_state_object['appliance_id'][0]['applianceType']
        power_on_actions = {}
        if appliance_type == "AC":
            power_on_actions = {
                "power": parental_control['power_on']['actions']['power'],
                "mode": parental_control['power_on']['actions']['mode'],
                "temperature": parental_control['power_on']['actions']['temp']
            }
        elif appliance_type == "ECONI":
            power_on_actions = {
                "power": parental_control['power_on']['actions']['power']
            }
        elif appliance_type == "LUMI":
            power_on_actions = {
                "power": parental_control['power_on']['actions']['power']
            }
        parental_control_object = {
            "powerOn": {
                "startTime": parental_control['power_on']['start_time'],
                "endTime": parental_control['power_on']['end_time'],
                "isEnabled": parental_control['power_on']['is_enabled'],
                "actions": power_on_actions
            },
            "powerOff": {
                "startTime": parental_control['power_off']['start_time'],
                "endTime": parental_control['power_off']['end_time'],
                "isEnabled": parental_control['power_off']['is_enabled']
            }
        }
    return parental_control_object


def create_response_object(device_id, device_name, device_type, device_type_version, broadcast_name, application_type,
                           application_version, fw_version, device_time_zone, applianceObject, device_coordinates,
                           deviceStatus, is_energy_device_val, latestactions, mac_address, units, wifi_name, user_id,
                           instCurr, usageToday, usage_timestamp, costToday, avgDaily, estMonthly, latEnvVar, thingArn,
                           certificateId, certificateArn, certificatePem, keyPair, created_at, completedSeconds, is_blocked,
                           block_message, device_settings, parental_control_object, group_id, device_image_url,
                           device_filter_duration, device_filter_flag):
    if 'moderules' not in latestactions:
        latestactions["moderules"] = "default:default:default"
        latestactions["uirules"] = "default:default:default"
    device_object = {
        "deviceId": device_id,
        "deviceName": device_name,
        "deviceType": device_type,
        "deviceTypeVersion": device_type_version,
        "broadcastName": broadcast_name,
        'application_type': application_type,
        'application_version': application_version,
        "fwVersion": fw_version,
        "deviceTimeZone": device_time_zone,
        "applianceIdList": applianceObject,
        "deviceCoordinates": device_coordinates,
        "deviceStatus": str(deviceStatus),
        "isBlocked": is_blocked,
        "blockMessage": block_message,
        "isEnergyDevice": str(is_energy_device_val),
        "latestAction": latestactions,
        "macAddress": mac_address,
        "totalUnits": str(units),
        "wifiName": wifi_name,
        "userId": user_id,
        "instantaneousCurrent": instCurr,
        "usageToday": usageToday,
        "usageTimestamp": usage_timestamp,
        "offlineDuration": "0",
        "costToday": costToday,
        "avgDaily": avgDaily,
        "estMonthly": estMonthly,
        "latEnvVar": latEnvVar,
        "completedSeconds": str(completedSeconds),
        "thingArn": thingArn,
        "certificateId": certificateId,
        "certificateArn": certificateArn,
        "certificatePem": certificatePem,
        "keyPair": keyPair,
        "createdAt": str(created_at),
        "deviceSettings": device_settings,
        "parentalControl": parental_control_object,
        "groupId": group_id,
        "deviceImageURL": device_image_url,
        "filterDuration": device_filter_duration,
        "filterFlag": device_filter_flag
    }
    return device_object
