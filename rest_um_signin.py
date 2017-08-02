import boto3
import json

from imports.models.central_system import CentralSystem
from imports.models.installations import Installations
from imports.models.device_state import DeviceState
from boto3.dynamodb.conditions import Key
from imports.models.user import User
from imports.user_level import UserLevel
from imports.constants import Constants
from imports.defaults import Defaults
from imports.response import Response
from imports.table import Table
from lib.cutomjtw import CustomJWT
from util.util import Util

lambdaClient = boto3.client('lambda')

"""
__author__      = Umair Ansari
__copyright__   = Copyright 2007, Cielo WiGle
__date__        = 25, April 2017
__version__     = 1.0.0
"""

# This comment is to test automation

def lambda_handler(event, context):
    """

    :param event: [user_id, password, mobile_device_id, device_token_id, app_type, app_version, time_zone, mobile_device_name ]
    :param context: []
    :return: 200 for success, 400 for missing parameter values, 500 if code crashes, 401 if unauthorized

    @about: 1. validate all incoming parameters, return 400 if missing
            2. validate username, password, return 401 if fails to validate
            3. verify notification_blocked status from installation table
            4. call another lambda function "TestInstallation" , return 500 in fails
            5. create JTW token for this user
            6. create and send back response
    """
    # from User models
    user_id = event.get(User.USER_ID, "").strip()
    password = event.get(User.PASSWORD, "").strip()

    # from installations models
    mobile_device_id = event.get(Installations.MOBILE_DEVICE_ID, "").strip()
    device_token_id = event.get(Installations.DEVICE_TOKEN_ID, "").strip()
    app_type = event.get(Installations.APP_TYPE, "").strip()
    app_version = event.get(Installations.APP_VERSION, "").strip()
    time_zone = event.get(Installations.TIME_ZONE, "").strip()
    mobile_device_name = event.get(Installations.MOBILE_DEVICE_NAME, "").strip()

    response = Response()
    central_system = Defaults.CENTRAL_SYSTEM[Constants.ENVIRONMENT]

    # 1. validate all incoming parameters, return 400 if missing
    if user_id != "" and password != "" and mobile_device_id != "" and device_token_id != "" and app_type != "" and app_version != "" and time_zone != "" and mobile_device_name != "":
        user_table = Table(User.USER_TABLE)
        util = Util()
        users = user_table.get_item_by_key({User.USER_ID: user_id})

        # 2. validate username, password, return 409 if fails to validate
        if users is None or util.decode_base64(users.get(User.PASSWORD, "")) != password:
            raise Exception(response.get_custom_exception(Constants.UNAUTHORIZED, Constants.USERNAME_PASSWORD_MISMATCH))

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

        # 3. verify notification_blocked status from installation table
        installation = Table(Installations.INSTALLATIONS_TABLE).get_item_by_key({User.USER_ID: user_id, Installations.MOBILE_DEVICE_ID: mobile_device_id})
        # 4. call another lambda function "TestInstallation" , return 500 in fails
        try:
            lambdaClient.invoke(FunctionName='TestInstallation', InvocationType='Event ', LogType='Tail',
                                Payload=json.dumps(payload))
        except Exception as e:
            util.log(e)

        # 6. create and send back response
        response_object = {
            User.USER_ID: user_id,
            User.EMAIL_ID: users[User.EMAIL_ID],
            User.IS_EMAIL_VERIFIED: users[User.IS_EMAIL_VERIFIED],
            User.CONTACT_NO: users[User.CONTACT_NO],
            User.USER_IMAGE_URL: users.get(User.USER_IMAGE_URL, None),
            User.USER_COVER_URL: users.get(User.USER_COVER_URL, None),
            DeviceState.DEVICE_COUNT: Table(DeviceState.DEVICE_STATE).get_item_via_query_count(Key(User.USER_ID).eq(user_id), Constants.USER_ID_INDEX),
            Installations.NOTIFICATION_BLOCKED: Constants.BLOCKED if installation is None else int(installation[Installations.NOTIFICATION_BLOCKED]),
            User.CURRENCY_SYMBOL:  users[User.CURRENCY_SYMBOL] if users.has_key(User.CURRENCY_SYMBOL) else CentralSystem[CentralSystem.DEFAULT_CURRENCY_SYMBOL],
            User.CURRENT_SYSTEM_ORIENTATION: float(users[User.CURRENT_SYSTEM_ORIENTATION] if users.has_key(User.CURRENT_SYSTEM_ORIENTATION) else CentralSystem[CentralSystem.DEFAULT_CURRENT_SYSTEM_ORIENTATION]),
            User.UNIT_PRICE: float(users[User.UNIT_PRICE] if users.has_key(User.UNIT_PRICE) else CentralSystem[CentralSystem.DEFAULT_UNIT_PRICE]),
            User.DEV_CURRENCY_INDEX: float(users[User.DEV_CURRENCY_INDEX] if users.has_key(User.DEV_CURRENCY_INDEX) else CentralSystem[CentralSystem.DEFAULT_CURRENCY_INDEX]),
            User.IS_DEFAULT: users[User.IS_DEFAULT] if users.has_key(User.IS_DEFAULT) else Constants.DEFAULT_INT,
            # 5. create JTW token for this user
            Constants.TOKEN: CustomJWT().get_token(user_id, Constants.JWT_ONE_DAY, Constants.JWT_SECRET, Constants.JWT_ALGO),
            CentralSystem.IOS_VERSION: central_system[CentralSystem.IOS_VERSION],
            CentralSystem.ANDROID_VERSION_CODE: float(central_system[CentralSystem.ANDROID_VERSION_CODE]),
            CentralSystem.ANDROID_VERSION: central_system[CentralSystem.ANDROID_VERSION]
        }
        if app_type is Constants.WEB_APPLICATION:
            response_object.update({
                User.USER_LEVEL_INDEX: users.get(User.USER_LEVEL_INDEX, UserLevel().get_user_level_index(Constants.END_USER)),
                User.PARENT_USER: users.get(User.PARENT_USER, None)
            })
        return response.get_response(Constants.SUCCESS, Constants.SUCCESS, response_object)
    raise Exception(response.get_custom_exception(Constants.BAD_REQUEST, Constants.INVALID_JSON_FORMAT))
