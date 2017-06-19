import json

import boto3
from imports.models.central_system import CentralSystem
from imports.models.installations import Installations
from boto3.dynamodb.conditions import Key
from imports.models.user import User
from imports.user_level import UserLevel
from imports.constants import Constants
from imports.defaults import Defaults
from imports.response import Response
from imports.table import Table
from util.util import Util

lambdaClient = boto3.client('lambda')

"""
__author__      = Umair Ansari
__copyright__   = Copyright 2007, Cielo WiGle
__date__        = 25, April 2017
__version__     = 1.0.0
"""


def lambda_handler(event, context):
    """
    
    :param event: [user_id, password, email_id, mobile_device_id, device_token_id, app_type, app_version, time_zone, mobile_device_name, parent_user]
    :param context: []
    :return: 200 for success, 400 for missing parameter values, 500 if code crashes, 409 if conflict
    
    @about: 1. validate all incoming parameters, return 400 if missing
            2. validate username, email, password, return 400 if fails to validate
            3. verify username or email not exists in system, return 904 if exists
            4. save data in users table
            5. call another lambda function "TestInstallation" , return 500 if fails
            6. create and send back response
    """
    user_id = event.get(User.USER_ID, "").strip()
    password = event.get(User.PASSWORD, "").strip()
    email_id = event.get(User.EMAIL_ID, "").strip()
    parent_user = event.get(User.PARENT_USER, "").strip()

    mobile_device_id = event.get(Installations.MOBILE_DEVICE_ID, "").strip()
    device_token_id = event.get(Installations.DEVICE_TOKEN_ID, "").strip()
    app_type = event.get(Installations.APP_TYPE, "").strip()
    app_version = event.get(Installations.APP_VERSION, "").strip()
    time_zone = event.get(Installations.TIME_ZONE, "").strip()
    mobile_device_name = event.get(Installations.MOBILE_DEVICE_NAME, "").strip()

    response = Response()
    util = Util()
    user_level = UserLevel()
    central_system = Defaults.CENTRAL_SYSTEM[Constants.ENVIRONMENT]

    # 1. validate all incoming parameters, return 400 if missing
    if user_id != "" and password != "" and email_id != "" and mobile_device_id != "" and device_token_id != "" and app_type != "" and app_version != "" and time_zone != "" and mobile_device_name != "" and parent_user != "" :

        # 2. validate username, email, password, return 400 if fails to validate
        validation = util.validate(user_id, email_id, password)
        if validation is not None:
            raise Exception(validation)

        user_table = Table(User.USER_TABLE)

        # TODO : True means email is verified, please make it false here and perform proper email validation
        is_email_verified = True

        # 3. verify username or email not exists in system, return 904 if exists
        if user_table.get_item_by_key({User.USER_ID: user_id}) is not None:
            raise Exception(response.get_custom_exception(Constants.CONFLICT, Constants.USERNAME_ALREADY_EXISTS))
        if user_table.get_item_via_query(Key(User.EMAIL_ID).eq(email_id), User.USER_EMAIL_INDEX) is not None:
            raise Exception(response.get_custom_exception(Constants.CONFLICT, Constants.EMAIL_ALREADY_EXISTS))

        password_base64 = Util().encode_base64(password)    # convert to base 64

        # 4. save data in users table
        user_table.put_item({
                User.USER_ID: user_id,
                User.EMAIL_ID: email_id,
                User.PASSWORD: password_base64,
                User.IS_SOCIAL_MEDIA: Constants.DEFAULT_INT,       # 0
                User.IS_EMAIL_VERIFIED: is_email_verified,
                User.CREATED_AT: Util().get_current_time_utc(),    # getting current time in utc
                User.CONTACT_NO: Constants.DEFAULT_STRING,     # default string ""
                User.USER_IMAGE_PATH: Constants.DEFAULT_STRING,
                User.CURRENCY_SYMBOL: central_system[CentralSystem.DEFAULT_CURRENCY_SYMBOL],
                User.CURRENT_SYSTEM_ORIENTATION: central_system[CentralSystem.DEFAULT_CURRENT_SYSTEM_ORIENTATION],
                User.UNIT_PRICE: central_system[CentralSystem.DEFAULT_UNIT_PRICE],
                User.DEV_CURRENCY_INDEX: central_system[CentralSystem.DEFAULT_CURRENCY_INDEX],
                User.USER_LEVEL_INDEX: user_level.get_user_level_index(Constants.END_USER),
                User.PARENT_USER: parent_user,
                User.USER_LEVEL: user_level.get_user_level_name(Constants.END_USER),   # for new users, users level will be 4
                User.IS_DELETED: Constants.DEFAULT_INT,    # 0
                User.IS_DEFAULT: Constants.DEFAULT_INT     # 0
            }
        )


        # TODO : after new version of TestInstallation please update these variables name, as these will not work, thy are in camel notation
        payload = {
            "mobileDeviceId": mobile_device_id,
            "deviceTokenId": device_token_id,
            "appType": app_type,
            "appVersion": app_version,
            "timeZone": time_zone,
            "deviceName": mobile_device_name,
            "userId": user_id
        }

        # 5. call another lambda function "TestInstallation" , return 500 in fails
        try:
            lambdaClient.invoke(FunctionName='TestInstallation', InvocationType='Event ', LogType='Tail', Payload=json.dumps(payload))
        except Exception as e:
            util.log(e)

        # 6. create and send back response
        response_object = {
            User.USER_ID: user_id,
            User.EMAIL_ID: email_id,
            User.CREATED_AT: util.get_current_time_utc(),
            User.IS_EMAIL_VERIFIED: is_email_verified,
            Installations.NOTIFICATION_BLOCKED: Constants.BLOCKED,  # 1
            User.USER_IMAGE_URL: central_system[CentralSystem.PROFILE_IMAGE_URL],
            User.CURRENCY_SYMBOL: central_system[CentralSystem.DEFAULT_CURRENCY_SYMBOL],
            User.CURRENT_SYSTEM_ORIENTATION: central_system[CentralSystem.DEFAULT_CURRENT_SYSTEM_ORIENTATION],
            User.UNIT_PRICE: central_system[CentralSystem.DEFAULT_UNIT_PRICE],
            User.DEV_CURRENCY_INDEX: central_system[CentralSystem.DEFAULT_CURRENCY_INDEX],
            User.USER_LEVEL_INDEX: user_level.get_user_level_name(Constants.END_USER),
            User.PARENT_USER: parent_user,
            User.IS_DEFAULT: Constants.DEFAULT_INT,  # 0
            CentralSystem.IOS_VERSION: central_system[CentralSystem.IOS_VERSION],
            CentralSystem.ANDROID_VERSION_CODE: float(central_system[CentralSystem.ANDROID_VERSION_CODE]),
            CentralSystem.ANDROID_VERSION: central_system[CentralSystem.ANDROID_VERSION]
            }
        return response.get_response(Constants.SUCCESS, Constants.SUCCESS, response_object)
    raise Exception(response.get_custom_exception(Constants.BAD_REQUEST, Constants.INVALID_JSON_FORMAT))



