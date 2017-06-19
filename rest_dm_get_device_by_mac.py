from imports.models.central_system import CentralSystem
from imports.models.device_state import DeviceState
from imports.models.devices import Devices
from imports.constants import Constants
from imports.defaults import Defaults
from imports.response import Response
from imports.table import Table

"""
__author__      = Umair Ansari
__copyright__   = Copyright 2007, Cielo WiGle
__date__        = 26, May 2017
__version__     = 1.0.0
"""


def lambda_handler(event, context):
    central_sys_item = Defaults.CENTRAL_SYSTEM[Constants.ENVIRONMENT]

    mac_address = event.get('mac_address', "")
    created_at = event.get('created_at', "")

    response = Response()
    if mac_address != "" and created_at != "":

        devices_table = Table(table_name=Devices.DEVICES_TABLE)
        if devices_table.get_table_object() is None:
            raise Exception(response.get_custom_exception(code=Constants.SERVER_ERROR, message=Constants.SERVER_ERROR))

        key = {'mac_address': mac_address, 'created_at': int(created_at)}
        device = devices_table.get_item_by_key(key=key)
        if device is None:
            raise Exception(response.get_custom_exception(code=Constants.NOT_FOUND, message=Constants.NOT_FOUND))

        device_state_table = Table(table_name=DeviceState.DEVICE_STATE)
        if device_state_table.get_table_object() is None:
            raise Exception(response.get_custom_exception(code=Constants.SERVER_ERROR, message=Constants.SERVER_ERROR))
        key = {'mac_address': mac_address}
        device_state = device_state_table.get_item_by_key(key=key)

        if device_state is None:
            raise Exception(response.get_custom_exception(code=Constants.SERVER_ERROR, message=Constants.SERVER_ERROR))

        device_object = {}
        if device_state[DeviceState.DEVICE_ID] == device[Devices.DEVICE_ID]:

            # Make parental control object
            parental_control_object = get_parental_control_object(device_state_object=device_state)

            # Get group_id if exists else send None(null)
            group_id = device.get(Devices.GROUP_ID, None)
            # Get custom device image
            device_image_url = device_state.get(DeviceState.DEVICE_IMAGE_URL, None)
            # AC filter
            device_filter_duration = device_state.get(DeviceState.DEVICE_FILTER_DURATION, 0)
            # Convert filter duration from seconds to hours
            device_filter_duration = round(device_filter_duration / 3600, 2)
            device_filter_flag = device_state.get(DeviceState.DEVICE_FILTER_FLAG, 1)
            user_id = device_state[DeviceState.DEVICE_ID]
            device_object = create_response_object(
                device_id=device[Devices.DEVICE_ID],
                device_name=device[Devices.DEVICE_NAME],
                device_type=device[Devices.DEVICE_TYPE],
                device_type_version=device["device_type_version"],
                broadcast_name=device["broadcast_name"],
                fw_version=device["fw_version"],
                device_time_zone=device["device_time_zone"],
                appliance_object=device["appliance_id"],
                device_status=device_state["device_status"],
                latest_actions=device_state["latest_action"],
                mac_address=device["mac_address"],
                wifi_name=device_state["wifi_name"],
                user_id=user_id,
                created_at=device["created_at"],
                parental_control_object=parental_control_object,
                group_id=group_id,
                device_image_url=device_image_url,
                device_filter_duration=device_filter_duration,
                device_filter_flag=device_filter_flag)

        response_object = {
            CentralSystem.IOS_VERSION: central_sys_item[CentralSystem.IOS_VERSION],
            CentralSystem.ANDROID_VERSION: central_sys_item[CentralSystem.ANDROID_VERSION],
            'device_state': device_object
        }
        return response.get_response(code=Constants.SUCCESS, message=Constants.SUCCESS, data=response_object)
    raise Exception(response.get_custom_exception(code=Constants.BAD_REQUEST, message=Constants.INVALID_JSON_FORMAT))


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


def create_response_object(device_id, device_name, device_type, device_type_version, broadcast_name, fw_version,
                           device_time_zone, appliance_object, device_status, latest_actions, mac_address, wifi_name, user_id,
                           created_at, parental_control_object, group_id, device_image_url, device_filter_duration,
                           device_filter_flag):
    if 'moderules' not in latest_actions:
        latest_actions["moderules"] = "default:default:default"
        latest_actions["uirules"] = "default:default:default"
    device_object = {
        "deviceId": device_id,
        "deviceName": device_name,
        "deviceType": device_type,
        "deviceTypeVersion": device_type_version,
        "broadcastName": broadcast_name,
        "fwVersion": fw_version,
        "deviceTimeZone": device_time_zone,
        "applianceIdList": appliance_object,
        "deviceStatus": str(device_status),
        "latestAction": latest_actions,
        "macAddress": mac_address,
        "wifiName": wifi_name,
        "userId": user_id,
        "createdAt": str(created_at),
        "parentalControl": parental_control_object,
        "groupId": group_id,
        "deviceImageURL": device_image_url,
        "filterDuration": device_filter_duration,
        "filterFlag": device_filter_flag
    }
    return device_object
