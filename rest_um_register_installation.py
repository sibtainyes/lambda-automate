import boto3
import json

from imports.models.installations import Installations
from imports.constants import Constants
from imports.response import Response
from imports.table import Table
from util.util import Util

sns = boto3.client('sns')

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
    device_token_id = event.get(Installations.DEVICE_TOKEN_ID, "").strip()
    app_type = event.get(Installations.APP_TYPE, "").strip()
    app_version = event.get(Installations.APP_VERSION, "").strip()
    time_zone = event.get(Installations.TIME_ZONE, "").strip()
    mobile_device_name = event.get(Installations.MOBILE_DEVICE_NAME, "").strip()
    user_id = event.get(Installations.USER_ID, "").strip()
    mobile_device_id = event.get(Installations.MOBILE_DEVICE_ID, "").strip()

    response = Response()

    if device_token_id != "" and app_type != "" and app_version != "" and time_zone != "" and mobile_device_name != "" and user_id != "" and mobile_device_id != "" and (app_type == Constants.IOS_APPLICATION or app_type == Constants.ANDROID_APPLICATION):
        application_id = Constants.SNS_APPLICATION[app_type]
        installation_table = Table(Installations.INSTALLATIONS_TABLE)

        installation = installation_table.get_item_by_key({Installations.USER_ID: user_id, Installations.DEVICE_TOKEN_ID: device_token_id})
        if installation is not None:
            end_point_arn = installation[Installations.END_POINT_ARN]

            sns_response = sns.get_endpoint_attributes(
                EndpointArn=end_point_arn
            )
            if len(sns_response['Attributes']) != 0:
                enabled = sns_response['Attributes']['Enabled']
                token = sns_response['Attributes']['Token']
                customer_user_data = sns_response['Attributes']['CustomUserData']
                if enabled != 'true' and token != device_token_id and customer_user_data != mobile_device_name:
                    sns.set_endpoint_attributes(
                        EndpointArn=end_point_arn,
                        Attributes={
                            'CustomUserData': mobile_device_name,
                            'Enabled': 'true',
                            'Token': device_token_id
                        }
                    )
                return response.get_response(Constants.SUCCESS, Constants.SUCCESS)
            else:
                response_sns_create = sns.create_platform_endpoint(
                    PlatformApplicationArn=application_id,
                    Token=device_token_id,
                    CustomUserData=mobile_device_name
                )
                end_point_arn = response_sns_create[Installations.END_POINT_ARN]
                result = installation_table.update_item_by_key(
                    {Installations.USER_ID: user_id, Installations.DEVICE_TOKEN_ID: device_token_id},
                    "set app_type = :appType, app_version = :appVersion,  time_zone = :timeZone, mobile_device_name= :deviceName, end_point_arn=:endPointArn",
                    {
                        ':deviceTokenId': device_token_id,
                        ':appType': app_type,
                        ':appVersion': app_version,
                        ':timeZone': time_zone,
                        ':deviceName': mobile_device_name,
                        ':endPointArn': end_point_arn
                    },
                    "UPDATED_NEW",
                    "device_token_id = :deviceTokenId")

                return response.get_response(Constants.SUCCESS, Constants.SUCCESS)
        else:
            response_sns_create = sns.create_platform_endpoint(
                PlatformApplicationArn=application_id,
                Token=device_token_id,
                CustomUserData=mobile_device_name
            )
            end_point_arn = response_sns_create["EndpointArn"]
            installation_table.put_item(
                {
                    Installations.DEVICE_TOKEN_ID: device_token_id,
                    Installations.APP_TYPE: app_type,
                    Installations.APP_VERSION: app_version,
                    Installations.TIME_ZONE: time_zone,
                    Installations.MOBILE_DEVICE_NAME: mobile_device_name,
                    Installations.END_POINT_ARN: end_point_arn,
                    Installations.CREATED_DATE: Util().get_current_time_utc(),
                    Installations.USER_ID: user_id,
                    Installations.NOTIFICATION_BLOCKED: Constants.BLOCKED
                }
            )
            return response.get_response(Constants.SUCCESS, Constants.SUCCESS)
    raise Exception(response.get_custom_exception(Constants.BAD_REQUEST, Constants.INVALID_JSON_FORMAT))
