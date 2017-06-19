from imports.models.device_state import DeviceState
from boto3.dynamodb.conditions import Key, Attr
from imports.models.actions import Actions
from imports.constants import Constants
from imports.response import Response
from imports.table import Table
from util.util import Util
from datetime import datetime
import json, boto3

snsClient = boto3.client('sns')


"""
__author__      = Umair Ansari
__copyright__   = Copyright 2007, Cielo WiGle
__date__        = 26, May 2017
__version__     = 1.0.0
"""


def lambda_handler(event, context):

    application_coordinates = event.get('application_coordinates', "")
    communication_source = event.get('communication_source', "")
    application_version = event.get('application_version', "")
    device_coordinates = event.get('device_coordinates', "")
    device_created_at = event.get('device_created_at', "")
    action_timestamp = event.get('action_timestamp', "")
    mobile_device_id = event.get('mobileDeviceId', "")
    action_source = event.get('action_source', "")
    action_value = event.get('action_value', "")
    appliance_id = event.get('appliance_id', "")
    action_type = event.get('action_type', "")
    mac_address = event.get('mac_address', "")
    device_id = event.get('device_id', "")
    user_id = event.get('user_id', "")

    response = Response()
    if application_coordinates != "" and communication_source != "" and application_version != "" and device_coordinates != "" and device_created_at != "" and isinstance(action_timestamp, int) and action_timestamp != 0 and mobile_device_id != "" and action_source != "" and action_value != "" and appliance_id != "" and action_type != "" and mac_address != "" and device_id != "" and user_id != "" :

        device_state_table = Table(DeviceState.DEVICE_STATE)
        if device_state_table.get_table_object() is None:
            raise Exception(response.get_custom_exception(code=Constants.SERVER_ERROR, message=Constants.SERVER_ERROR))

        key = {'mac_address': mac_address}
        device_state = device_state_table.get_item_by_key(key=key)
        if device_state is None:
            raise Exception(response.get_custom_exception(code=Constants.NOT_FOUND, message=Constants.NOT_FOUND))

        timestamp = device_state["latest_action"]["timestamp"]

        utc_ts = Util().get_current_time_utc()
        if action_type in device_state["latest_action"]:
            latest_action = device_state["latest_action"][action_type]
        else:
            device_state["latest_action"][action_type] = None
            latest_action = device_state["latest_action"][action_type]
        if (action_type != 'power' and device_state["latest_action"]['power'] == 'on' and latest_action != action_value) or (action_type == 'power' and latest_action != action_value):

            action_table = Table(Actions.ACTIONS_TABLE)
            if action_type != 'rgb':
                item = {
                    "action_source": action_source,
                    "communication_source": communication_source,
                    "is_performed": 1,
                    "action_timestamp": action_timestamp,
                    "action_date": str(datetime.fromtimestamp(action_timestamp).strftime('%Y-%m-%d %H:%M:%S')),
                    "action_type": action_type,
                    "action_value": action_value,
                    "appliance_id": appliance_id,
                    "application_coordinates": application_coordinates,
                    "mobile_device_id": mobile_device_id,
                    "application_version": application_version,
                    "device_coordinates": device_coordinates,
                    "device_id": device_id,
                    "online_action_timestamp": "0",
                    "user_id": user_id,
                    "device_created_at": device_created_at
                }
                exception = action_table.put_item(item=item)
                if exception is not None:
                    raise Exception(response.get_custom_exception(code=Constants.SERVER_ERROR, message=Constants.SERVER_ERROR))
            if int(timestamp) < action_timestamp:
                device_state["latest_action"][action_type] = action_value
                device_state["latest_action"]["timestamp"] = str(action_timestamp)
                device_state["latest_action"]['device_status'] = 'on' if int(device_state["device_status"]) == 1 else 'off'

                key = {'mac_address': mac_address},
                update_expression = "set latest_action = :actionVal",
                expression_attribute_values = {':actionVal': device_state["Item"]["latest_action"]},
                return_values = "UPDATED_NEW"
                response = device_state_table.update_item_by_key(
                    key=key,
                    update_expression=update_expression,
                    expression_attribute_values=expression_attribute_values,
                    return_values=return_values
                )

            if int(action_timestamp) > utc_ts:
                generate_push_message(
                    action_type=action_type,
                    device_name=device_state["device_name"],
                    user_id=user_id,
                    description=action_value,
                    action_source=action_source,
                    mac_address=mac_address
                )

        return response.get_response(code=Constants.SUCCESS, message=Constants.SUCCESS)
    raise Exception(response.get_custom_exception(code=Constants.BAD_REQUEST, message=Constants.INVALID_JSON_FORMAT))


def generate_push_message(action_type, device_name, user_id, description, action_source, mac_address):
    if action_type == "power" or action_type == "mode" or action_type == "temp" or action_type == "fanspeed":
        message = ""
        action_source = action_source.split('/')
        source_type = action_source[0]

        message_end = " by "
        trigger_type = user_id
        if source_type != "iOS" and source_type != "Android" and source_type != "WEB":
            if source_type == "Heartbeat":
                source_type = "Remote"
            trigger_type = source_type
            message_end = " via "

        if len(action_source) > 1:
            trigger_type = action_source[1]
            message_end = " via "

        message_end += trigger_type + "."

        if action_type == "power":
            message += device_name + " turned " + description + message_end
        elif action_type == "temp":
            message += device_name + "'s temperature changed to " + description + message_end
        elif action_type == "mode":
            message += device_name + "'s mode changed to " + description + message_end
        elif action_type == "fanspeed":
            message += device_name + "'s fanspeed changed to " + description + message_end

        send_notification(user_id, mac_address, message)


def send_notification(user_id, mac_address, original_message):

    installation_table = Table('installations')

    key_condition_expression = Key('user_id').eq(user_id)
    filter_expression = Attr('notification_blocked').eq(1)

    installation_table_resp = installation_table.get_item_via_query(
        key_expression=key_condition_expression,
        filter_expression=filter_expression)

    central_sys_table = Table('central_sys')
    central_sys_table_resp = central_sys_table.get_item_by_key(key={'id': 1})
    ios_app = "APNS"
    android_app = "GCM"
    if 'Item' in central_sys_table_resp:
        ios_app = central_sys_table_resp["iOSSNSApp"]
        android_app = central_sys_table_resp["androidSNSApp"]

    for installation in installation_table_resp:
        message = original_message
        if installation["app_type"] == "iOS":
            payload = {
                ios_app: "{\"aps\":{\"alert\":\"" + message + "\",\"sound\":\"default\",\"macAddress\":\"" + mac_address + "\"}}"
            }
        elif installation["app_type"] == "Android":
            if 'mobile_device_id' in installation:
                message += "&" + installation["device_token_id"]
            payload = {
                android_app: "{\"data\":{\"message\":\"" + message + "\",\"macAddress\":\"" + mac_address + "\"}}"

            }
        try:
            response = snsClient.publish(
                TargetArn=installation["end_point_arn"],
                Message=json.dumps(payload),
                MessageStructure='json',
                MessageAttributes={
                    'mac_address':
                        {
                            'DataType': 'String',
                            'StringValue': mac_address
                        }
                }
            )
        except Exception, e:
            print(str(e))
