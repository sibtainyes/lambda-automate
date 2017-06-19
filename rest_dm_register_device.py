from imports.models.authentic_devices import AuthenticDevices
from imports.models.appliance_rules import ApplianceRules
from imports.models.appliance_codes import ApplianceCodes
from imports.models.device_state import DeviceState
from imports.models.appliance import Appliance
from imports.models.devices import Devices
from imports.models.things import Things
from imports.constants import Constants
from imports.response import Response
from imports.table import Table
from util.util import Util

from decimal import Decimal
from boto3.dynamodb.conditions import Key, Attr

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
    application_type = event.get('application_type', "")
    application_version = event.get('application_version', "")
    broadcast_name = event.get('broadcast_name', " ")  # I don't know the exactly reason of a single space
    device_name = event.get('device_name', "")
    device_time_zone = event.get('device_time_zone', "")
    codes_required = event['codes_required']
    is_return_req = event['is_return_required']
    mac_address = event.get('mac_address', "")
    user_id = event.get('user_id', "")
    device_coordinates = event.get('device_coordinates', "")
    appliance = event.get('appliance', "")
    applianceId = appliance['applianceId']
    wifi_name = event.get('wifi_name', "")

    if 'deviceRegion' in event:
        device_time_zone_name = event['device_time_zone_name']
        device_country = event['device_region']
    else:
        device_time_zone_name = device_time_zone
        device_country = 'Pakistan'

    response = Response()
    if broadcast_name != "" and isinstance(codes_required, int) and isinstance(is_return_req, int) and mac_address != "" and user_id != "" and device_coordinates != "" and appliance != "" and application_type != "" and application_version != "" and device_name != "" and device_time_zone != "" and device_country != "" and device_time_zone_name != "" and wifi_name != "" and isinstance(applianceId, int):
        util = Util()

        device_id = util.id_generator(6)
        authentic_devices_table = Table(AuthenticDevices.AUTHENTIC_DEVICES_TABLE)
        auth_table_response = authentic_devices_table.get_item_by_key({AuthenticDevices.MAC_ADDRESS: mac_address})
        if auth_table_response is None:
            raise Exception(response.get_custom_exception(Constants.UNAUTHORIZED, Constants.UNAUTHORIZED))

        else:
            devices_table = Table(Devices.DEVICES_TABLE)
            ke = Key(Devices.MAC_ADDRESS).eq(mac_address)
            fe = Attr(Devices.IS_REGISTERED).eq(1)
            device_count = devices_table.get_item_via_query_count(ke, None, fe)

            if device_count != 0:
                raise Exception(response.get_custom_exception(Constants.CONFLICT, Constants.CONFLICT))
            if device_count is None:
                raise Exception(response.get_custom_exception(Constants.SERVER_ERROR, Constants.SERVER_ERROR))
            else:

                created_at = util.get_current_time_utc()
                is_blocked_auth = int(auth_table_response[AuthenticDevices.IS_BLOCKED])

                if is_blocked_auth == 0:
                    auth_country = auth_table_response[AuthenticDevices.COUNTRY]
                    if auth_country.lower() == device_country.lower() or auth_country.lower() == "global":
                        device_type = auth_table_response[AuthenticDevices.DEVICE_TYPE]
                        device_type_version = auth_table_response[AuthenticDevices.DEVICE_TYPE_VERSION]
                        fw_version = auth_table_response[AuthenticDevices.FW_VERSION]
                        is_energy_device = auth_table_response[AuthenticDevices.IS_ENERGY_DEVICE]
                        is_blocked = 0
                        block_message = "Unblocked"
                        device_type = device_type.replace("\"", '')

                        is_energy_device_val = 1 if is_energy_device else 0

                        devices_table.put_item(
                            {
                                Devices.APPLIANCE_ID_LIST: [{
                                    Devices.APPLIANCE_ID_DICT[Devices.APPLIANCE_ID]: str(appliance[Devices.APPLIANCE_ID_DICT[Devices.APPLIANCE_ID]]),
                                    Devices.APPLIANCE_ID_DICT[Devices.APPLIANCE_TYPE]: appliance[Devices.APPLIANCE_ID_DICT[Devices.APPLIANCE_TYPE]]
                                }],
                                Devices.APPLICATION_TYPE: application_type,
                                Devices.APPLICATION_VERSION: application_version,
                                Devices.BROADCAST_NAME: broadcast_name,
                                Devices.DEVICE_ID: device_id,
                                Devices.DEVICE_NAME: device_name,
                                Devices.DEVICE_TIME_ZONE: device_time_zone,
                                Devices.MAC_ADDRESS: mac_address,
                                Devices.USER_ID: user_id,
                                Devices.CREATED_AT: int(created_at),
                                Devices.UPDATE_AT: int(created_at),
                                Devices.DEVICE_COORDINATES: device_coordinates,
                                Devices.DEVICE_TYPE: device_type,
                                Devices.DEVICE_TYPE_VERSION: device_type_version.replace("\"", ''),
                                Devices.FW_VERSION: fw_version.replace("\"", ''),
                                Devices.IS_ENERGY_DEVICE: is_energy_device_val,
                                Devices.IS_REGISTERED: 1,
                                Devices.WIFI_NAME: wifi_name,
                                Devices.IS_BLOCKED: is_blocked,
                                Devices.BLOCK_MESSAGE: block_message
                            }
                        )

                        is_faren = 0

                        # Parental_Control
                        # Calculate hours, minutes and offset from device timezone
                        device_time_zone_offset = device_time_zone[0]
                        device_time_zone_time = device_time_zone[1:].split(':')
                        device_time_zone_hour = int(device_time_zone_time[0])
                        device_time_zone_minute = int(device_time_zone_time[1])

                        default_power_on_start_utc = util.convert_to_utc(
                            Constants.DEFAULT_POWER_ON_START,
                            device_time_zone_offset,
                            device_time_zone_hour,
                            device_time_zone_minute)

                        default_power_on_end_utc = util.convert_to_utc(
                            Constants.DEFAULT_POWER_ON_END,
                            device_time_zone_offset,
                            device_time_zone_hour,
                            device_time_zone_minute)

                        default_power_off_start_utc = util.convert_to_utc(
                            Constants.DEFAULT_POWER_OFF_START,
                            device_time_zone_offset,
                            device_time_zone_hour,
                            device_time_zone_minute)

                        default_power_off_end_utc = util.convert_to_utc(
                            Constants.DEFAULT_POWER_OFF_END,
                            device_time_zone_offset,
                            device_time_zone_hour,
                            device_time_zone_minute)

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
                        power_on_actions = {}

                        appliance_table = Table(Appliance.APPLIANCE_TABLE)
                        key = {
                            Appliance.APPLIANCE_ID: int(appliance[Devices.APPLIANCE_ID_DICT[Devices.APPLIANCE_ID]])
                        }
                        appliance = appliance_table.get_item_by_key(key)
                        if appliance is not None and Appliance.IS_FAREN in appliance:
                            is_faren = appliance[Appliance.IS_FAREN]
                        if appliance[Devices.APPLIANCE_TYPE_LIST] == "AC":

                            temp = "78" if is_faren == 1 else "26"

                            latest_actions = {
                                "power": "off",
                                "temp": temp,
                                "mode": "cool",
                                "fan_speed": "high",
                                "swing": "pos1",
                                "timestamp": created_at,
                                "status_timestamp": created_at
                            }
                            lat_env = {
                                "temperature": "0",
                                "humidity": "0"
                            }
                            power_on_actions = {
                                "power": "on",
                                "temperature": temp,
                                "mode": "cool"
                            }
                        elif appliance[Devices.APPLIANCE_ID_DICT[Devices.APPLIANCE_TYPE]] == "wili":
                            latest_actions = {
                                "power": "off",
                                "dimmer": "100",
                                "timestamp": created_at,
                                "status_timestamp": created_at
                            }
                            lat_env = {
                                "instantaneous_current": "0",
                                "total_units": "0.0"
                            }
                        elif appliance[Devices.APPLIANCE_ID_DICT[Devices.APPLIANCE_TYPE]] == "ECONI":
                            latest_actions = {
                                "power": "off",
                                "timestamp": created_at,
                                "status_timestamp": created_at
                            }
                            lat_env = {
                                "instantaneous_current": "0", "total_units": "0.0"
                            }
                            power_on_actions = {
                                "power": "on"
                            }
                        elif appliance[Devices.APPLIANCE_ID_DICT[Devices.APPLIANCE_TYPE]] == "LUMI":
                            latest_actions = {
                                "power": "on",
                                "rgb": "0,0,0,255,0,100,1",
                                "timestamp": created_at,
                                "status_timestamp": created_at
                            }
                            lat_env = {
                                "instantaneous_current": "0",
                                "total_units": "0.0"
                            }
                            power_on_actions = {
                                "power": "on",
                                # "rgb" : "0,0,0,255,0,100,1"
                            }
                        else:
                            latest_actions = {
                                "power": "off",
                                "status_timestamp": created_at
                            }
                            lat_env = {}
                            power_on_actions = {}

                        # Make parental control object
                        power_on.update({"actions": power_on_actions})
                        parental_control = {
                            "powerOn": power_on,
                            "powerOff": power_off
                        }

                        thing_arn = None
                        certificate_id = None
                        certificate_arn = None
                        certificate_pem = None
                        key_pair = {'PrivateKey': None, 'PublicKey': None}

                        units = str(Decimal(0.00))
                        inst_curr = "0"
                        usage_today = "0"
                        usage_timestamp = created_at
                        cost_today = "0.0"
                        avg_daily = "0hr 0min"
                        est_monthly = "0.0"
                        lat_env_var = lat_env

                        device_status = "0"
                        device_settings = {}
                        if device_type == 'BREEZ':
                            device_settings["transmitter_value"] = '1111'
                            device_settings["brightness_value"] = '1'
                            device_settings["screenDisplay_value"] = '1'
                            device_settings["default_image"] = '1'

                        device_object = create_response_object(
                            device_id,
                            device_name,
                            device_type,
                            device_type_version.replace("\"", ''),
                            broadcast_name,
                            application_type,
                            application_version,
                            fw_version.replace("\"", ''),
                            device_time_zone,
                            [appliance],
                            device_coordinates,
                            device_status,
                            is_energy_device_val,
                            latest_actions,
                            mac_address,
                            units,
                            wifi_name,
                            user_id,
                            inst_curr,
                            usage_today,
                            usage_timestamp,
                            cost_today,
                            avg_daily,
                            est_monthly,
                            lat_env_var,
                            thing_arn,
                            certificate_id,
                            certificate_arn, certificate_pem, key_pair,
                            created_at, is_blocked, block_message, device_settings,
                            parental_control)
                        if is_return_req == 1:

                            devices_lst = [device_object]

                            things_table = Table(Things.THINGS_TABLE)
                            # get all registered devices for user
                            # user_id-is_registered-index
                            fe = Key(Devices.USER_ID).eq(user_id) & Key(Devices.IS_REGISTERED).eq(1)
                            device_list = devices_table.get_item_via_query(fe, Devices.USER_ID_IS_REGISTERED_INDEX)
                            if device_list is None:
                                raise Exception(
                                    response.get_custom_exception(Constants.SERVER_ERROR, Constants.SERVER_ERROR))

                            # get state of all registered devices for user
                            device_state_table = Table(DeviceState.DEVICE_STATE)
                            fe = Key(DeviceState.USER_ID).eq(user_id)
                            device_state_list = device_state_table.get_via_query(fe, DeviceState.USER_ID_INDEX)

                            if device_state_list is None:
                                raise Exception(
                                    response.get_custom_exception(Constants.SERVER_ERROR, Constants.SERVER_ERROR))

                            for device in device_list:

                                for device_state_object in device_state_list["Items"]:
                                    if device_state_object["device_id"] == device["device_id"]:

                                        # get things details for all registered devices for user
                                        if 'thing_arn' in device_state_object:
                                            fe = Attr('user_id').eq(user_id) & Attr('is_registered').eq(1)
                                            key = {
                                                Things.THING_MAC_ADDRESS: device_state_object["mac_address"],
                                                Things.THINGS_ARN: device_state_object["thing_arn"]
                                            }
                                            thing = things_table.get_item_by_key(key)
                                            if thing is not None:
                                                if thing["device_id"] == device["device_id"]:
                                                    thing_arn = thing["thing_arn"]
                                                    certificate_id = thing["certificate_id"]
                                                    certificate_arn = thing["certificate_arn"]
                                                    certificate_pem = thing["certificate_pem"]
                                                    key_pair = thing["key_pair"]

                                        # get latest environment variables
                                        if device["device_type"] == "wigle" or device["device_type"] == "BREEZ" or \
                                                        device["device_type"] == "BREEZ-I":
                                            if "lat_env_var" in device_state_object:
                                                lat_env = device_state_object["lat_env_var"]
                                            else:
                                                lat_env = {"temperature": "0", "humidity": "0"}
                                            usage_today = None
                                            usage_timestamp = None
                                            cost_today = None
                                            avg_daily = None
                                            est_monthly = None
                                        elif device["device_type"] == "ECONI":
                                            if "lat_env_var" in device_state_object:
                                                lat_env = device_state_object["lat_env_var"]
                                            else:
                                                lat_env = {"instantaneous_current": "0", "total_units": "0.0"}
                                            usage_today = device_state_object["usage_today"]
                                            usage_timestamp = device_state_object["usage_timestamp"]
                                            cost_today = device_state_object["cost_today"]
                                            avg_daily = "0hr 0min"
                                            est_monthly = "0.0"
                                        elif device["device_type"] == "LUMI":
                                            if "lat_env_var" in device_state_object:
                                                lat_env = device_state_object["lat_env_var"]
                                            else:
                                                lat_env = {"instantaneous_current": "0", "total_units": "0.0"}

                                            usage_today = device_state_object["usage_today"]
                                            usage_timestamp = device_state_object["usage_timestamp"]
                                            cost_today = device_state_object["cost_today"]
                                            avg_daily = "0hr 0min"
                                            est_monthly = "0.0"

                                        inst_curr = str(device_state_object['lat_env_var'][
                                                            "instantaneous_current"]) if "instantaneous_current" in \
                                                                                         device_state_object[
                                                                                             'lat_env_var'] else str(
                                            Decimal(0.00))
                                        total_units = str(
                                            device_state_object['lat_env_var']["total_units"]) if "total_units" in \
                                                                                                  device_state_object[
                                                                                                      'lat_env_var'] else str(
                                            Decimal(0.00))
                                        device_settings = device_state_object[
                                            "device_settings"] if 'device_settings' in device_state_object else {}
                                        lat_env_var = lat_env

                                        device_object = create_response_object(
                                            device[Devices.DEVICE_ID],
                                            device[Devices.DEVICE_NAME],
                                            device[Devices.DEVICE_TYPE],
                                            device[Devices.DEVICE_TYPE_VERSION],
                                            device[Devices.BROADCAST_NAME],
                                            device[Devices.APPLICATION_TYPE],
                                            device[Devices.APPLICATION_VERSION],
                                            device[Devices.FW_VERSION],
                                            device[Devices.DEVICE_TIME_ZONE],
                                            device["appliance_id"],
                                            device[Devices.DEVICE_COORDINATES],
                                            device_state_object["device_status"],
                                            device[Devices.IS_ENERGY_DEVICE],
                                            device_state_object["latest_action"],
                                            device[Devices.MAC_ADDRESS],
                                            str(total_units),
                                            device_state_object[Devices.WIFI_NAME],
                                            user_id,
                                            inst_curr,
                                            usage_today,
                                            usage_timestamp,
                                            cost_today,
                                            avg_daily,
                                            est_monthly,
                                            lat_env_var,
                                            thing_arn,
                                            certificate_id,
                                            certificate_arn,
                                            certificate_pem,
                                            key_pair,
                                            device[Devices.CREATED_AT],
                                            device[Devices.IS_BLOCKED],
                                            device[Devices.BLOCK_MESSAGE],
                                            device_settings,
                                            parental_control)

                                        devices_lst.append(device_object)
                            response_object = {
                                "list_device": devices_lst
                            }
                        else:
                            response_object = {
                                "device_object": device_object
                            }

                        if codes_required:
                            applianceId = int(applianceId)
                            appliance_codes_list = get_appliance_codes(applianceId)
                            appliance_rules_list = get_appliance_rules(applianceId)
                            response_object.update({'list_appliance_codes': appliance_codes_list,
                                                    'list_appliance_rules': appliance_rules_list})
                        return response.get_response(Constants.SUCCESS, Constants.SUCCESS, response_object)

                    else:
                        block_message = "Invalid device region. Please contact customer support."
                        if Util().block_device_by_mac_address(mac_address, block_message) is not None:
                            raise Exception(
                                response.get_custom_exception(Constants.FORBIDDEN, Constants.INVALID_JSON_FORMAT))
                        raise Exception(response.get_custom_exception(Constants.SERVER_ERROR, Constants.SERVER_ERROR))
                else:
                    raise Exception(response.get_custom_exception(Constants.FORBIDDEN, Constants.INVALID_JSON_FORMAT))

    raise Exception(response.get_custom_exception(Constants.BAD_REQUEST, Constants.INVALID_JSON_FORMAT))


def get_appliance_codes(appliance_id):
    appliance_code_table = Table(ApplianceCodes.APPLIANCE_CODE_TABLE)
    key = Key(ApplianceCodes.APPLIANCE_ID).eq(appliance_id)
    index = ApplianceCodes.APPLIANCE_ID_INDEX
    response = appliance_code_table.get_item_via_query(key, index)
    codes_list = []

    if response is not None:
        for code in response:
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
    response = appliance_rules_table.get_item_via_query_count(key, index)

    if response is not None:
        for rule in response:
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


def create_response_object(
        device_id,
        device_name,
        device_type,
        device_type_version,
        broadcast_name,
        application_type,
        application_version,
        fw_version,
        device_time_zone,
        appliance_object,
        device_coordinates,
        device_status,
        is_energy_device_val,
        latest_actions,
        mac_address,
        units,
        wifi_name,
        user_id,
        inst_curr,
        usage_today,
        usage_timestamp,
        cost_today,
        avg_daily,
        est_monthly,
        lat_env_var,
        thing_arn,
        certificate_id,
        certificate_arn,
        certificate_pem,
        key_pair,
        created_at,
        is_blocked,
        block_message,
        device_settings,
        parental_control
        ):
    device_object = {
        Devices.DEVICE_ID: device_id,
        Devices.DEVICE_NAME: device_name,
        Devices.DEVICE_TYPE: device_type,
        Devices.DEVICE_TYPE_VERSION: device_type_version,
        Devices.BROADCAST_NAME: broadcast_name,
        Devices.APPLIANCE_TYPE: application_type,
        Devices.APPLICATION_VERSION: application_version,
        Devices.FW_VERSION: fw_version,
        Devices.DEVICE_TIME_ZONE: device_time_zone,
        Devices.APPLIANCE: appliance_object,
        Devices.DEVICE_COORDINATES: device_coordinates,
        Devices.WIFI_NAME: wifi_name,
        Devices.USER_ID: user_id,
        Devices.MAC_ADDRESS: mac_address,
        Devices.IS_ENERGY_DEVICE: str(is_energy_device_val),

        DeviceState.DEVICE_STATE: str(device_status),

        "latest_action": latest_actions,
        "total_units": str(units),
        "instantaneous_current": inst_curr,
        "usage_today": usage_today,
        "usage_timestamp": usage_timestamp,
        "offline_duration": "0",
        "cost_today": cost_today,
        "avg_daily": avg_daily,
        "est_monthly": est_monthly,
        "lat_env_var": lat_env_var,
        "is_blocked": str(is_blocked),
        "block_message": block_message,
        "thing_arn": thing_arn,
        "certificate_id": certificate_id,
        "certificate_arn": certificate_arn,
        "certificate_pem": certificate_pem,
        "key_pair": key_pair,
        "created_at": str(created_at),
        "device_settings": device_settings,
        "parental_control": parental_control,
        "filter_duration": 0,
        "filter_flag": 1
    }
    return device_object

