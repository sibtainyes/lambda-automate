import datetime

from boto3.dynamodb.conditions import Key, Attr

from imports.constants import Constants
from imports.models.actions import Actions
from imports.models.device_state import DeviceState
from imports.response import Response
from imports.table import Table

actionSourceIndices = {
    "Remote": 0,
    "Collective Control": 1,
    "Location Tracking": 2,
    "Cloud": 3,
    "Apps": 4,
    "Switch": 6,
    "Schedule": 7,
    "CloudAction": 8,
    "Parental Control": 9,
    "Fota": {
        "upgraded": 10,
        "completed": 11
    }
}
# actionSourceIndices["Heartbeat"] = 5

"""
__author__      = Umair Ansari
__copyright__   = Copyright 2007, Cielo WiGle
__date__        = 26, May 2017
__version__     = 1.0.0
"""


def lambda_handler(event, context):
    exclusive_start_key = event['exclusive_start_key']
    direction = event['direction']
    device_id = event.get('device_id', "")
    user_id = event.get('user_id', "")
    limit = event['limit']
    # 0 if records less than given are to be sent and 1 if records greater than given exclusive key are to be sent
    # 0 in case of swipe up for smaller time records
    # 1 in case of swipe down for older records
    # if swipe down and direction 1 then actions returned must be less than current utc time

    response = Response()
    if device_id != "" and user_id != "" and exclusive_start_key != 0 and direction != 0 and limit != 0:

        if exclusive_start_key == 0:
            utc_ts = datetime.datetime.utcnow()
            exclusive_start_key = utc_ts
        if direction == 0:
            scan_index_forward = False
            # get records that are less than exclusive key
        else:
            scan_index_forward = True
            # get records that are greater than exclusive key
        device_state_table = Table(DeviceState.DEVICE_STATE)
        if device_state_table.get_table_object() is None:
            raise Exception(response.get_custom_exception(code=Constants.SERVER_ERROR, message=Constants.SERVER_ERROR))

        key_condition_expression = Key('device_id').eq(device_id)
        index_name = 'device_id-index',
        device_name = "cielo device"
        device_list = device_state_table.get_item_via_query(key_expression=key_condition_expression, index=index_name)

        if response is not None:
            device_name = device_list[0]["device_name"]

        ke = Key('device_id').eq(device_id)
        fe = Attr('user_id').eq(user_id) & Attr('is_performed').eq(1)

        actions_table = Table(Actions.ACTIONS_TABLE)
        exclusive_start_key = {
            'action_timestamp': int(exclusive_start_key),
            'device_id': device_id
        }

        actions_list = actions_table.get_table_object().query(
            KeyConditionExpression=ke,
            FilterExpression=fe,
            Limit=limit,
            ExclusiveStartKey=exclusive_start_key,
            ScanIndexForward=scan_index_forward
        )
        if actions_list["Count"] > 0:
            actions_list_arr = actions_list.get("Items", None)
        else:
            raise Exception(response.get_custom_exception(code=Constants.NOT_FOUND, message=Constants.NOT_FOUND))

        actions_lst = []
        if 'LastEvaluatedKey' in actions_list:
            last_evaluated_key = str(actions_list['LastEvaluatedKey']['action_timestamp'])
        else:
            last_evaluated_key = 0
        # Last Evaluated Key means there are no more records left to scan in that direction
        for action in actions_list_arr:
            action_date = str(
                datetime.datetime.fromtimestamp(int(action["action_timestamp"])).strftime('%Y-%m-%d %H:%M:%S'))
            communication_source = 'Cloud'
            if 'communication_source' in action:
                communication_source = action["communication_source"]
            if communication_source == 'C':
                communication_source = 'Cloud'
            action_source = action["action_source"]
            action_value = action["action_value"]
            if "initiated" not in action_value and "upgraded" not in action_value and "Heartbeat" not in action_source:
                action_source_index = 9
                if '/' in action_source:
                    action_source_indices = action_source.split('/')[1]
                    action_source_index = actionSourceIndices[action_source_indices]
                elif action_source in actionSourceIndices:
                    action_source_index = actionSourceIndices[action_source]
                elif action_source == 'Android' or action_source == 'iOS' or action_source == 'WEB':
                    action_source_index = actionSourceIndices["Apps"]
                elif action_source == 'Device':  # must be fota actions
                    action_source_index = actionSourceIndices["Fota"][action["action_value"]]

                if action["action_type"] == 'DeviceStatus':
                    action_value = action["action_value"] + 'line'

                action_object = {
                    Actions.DEVICE_ID: action[Actions.DEVICE_ID],
                    "action_value": action_value.title(),
                    Actions.ACTION_TYPE: action[Actions.ACTION_TYPE].title(),
                    Actions.APPLICATION_COORDINATES: action[Actions.APPLICATION_COORDINATES],
                    Actions.ACTION_TIMESTAMP: int(action[Actions.ACTION_TIMESTAMP]),
                    Actions.APPLICATION_VERSION: action[Actions.APPLICATION_VERSION],
                    Actions.APPLIANCE_ID: action[Actions.APPLIANCE_ID],
                    Actions.DEVICE_COORDINATES: action[Actions.DEVICE_COORDINATES],
                    Actions.USER_ID: action[Actions.USER_ID],
                    "action_date": action_date,
                    "communication_source": communication_source,
                    "action_source": action_source,
                    "action_source_index": action_source_index,
                    "device_name": device_name
                }
                actions_lst.append(action_object)
        response_object = {
            'no_of_records': str(len(actions_lst)),
            'list_of_actions': actions_lst,
            'last_evaluated_key': last_evaluated_key
        }
        return response.get_response(code=Constants.SUCCESS, message=Constants.SUCCESS, data=response_object)
    raise Exception(response.get_custom_exception(code=Constants.BAD_REQUEST, message=Constants.INVALID_JSON_FORMAT))
