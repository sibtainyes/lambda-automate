import json
import boto3

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
    
    :param event: [user_id, password, email_id, parent_user]
    :param context: [] 
    :return: 
    """
    # from User Model
    user_id = event.get(User.USER_ID, "").strip()
    password = event.get(User.PASSWORD, "").strip()
    email_id = event.get(User.EMAIL_ID, "").strip()
    parent_user = event.get(User.PARENT_USER, "").strip()

    # from installations models
    mobile_device_id = event.get(Installations.MOBILE_DEVICE_ID, "").strip()
    device_token_id = event.get(Installations.DEVICE_TOKEN_ID, "").strip()
    app_type = event.get(Installations.APP_TYPE, "").strip()
    app_version = event.get(Installations.APP_VERSION, "").strip()
    time_zone = event.get(Installations.TIME_ZONE, "").strip()
    mobile_device_name = event.get(Installations.MOBILE_DEVICE_NAME, "").strip()

    response = Response()
    if user_id != "" and password != "" and email_id != "" and mobile_device_id != "" and device_token_id != "" and app_type != "" and app_version != "" and time_zone != "" and mobile_device_name != "" and parent_user != "":

        user_table = Table(User.USER_TABLE)
        central_system = Defaults.CENTRAL_SYSTEM[Constants.ENVIRONMENT]
        util = Util()

        currency_symbol = central_system[CentralSystem.DEFAULT_CURRENCY_SYMBOL]
        cur_sym_orientation = central_system[CentralSystem.DEFAULT_CURRENT_SYSTEM_ORIENTATION]
        currency_index = central_system[CentralSystem.DEFAULT_CURRENCY_INDEX]
        unit_price = central_system[CentralSystem.DEFAULT_UNIT_PRICE]

        # TODO : True means email is verified, please make it false here and perform proper email validation
        is_email_verified = True
        is_default = Constants.DEFAULT_INT
        user_level_index = UserLevel().get_user_level_index(Constants.END_USER)  # 4

        if user_table.get_item_by_key({User.USER_ID: user_id}) is not None:
            raise Exception(response.get_custom_exception(Constants.CONFLICT, Constants.CONFLICT))
        if user_table.get_item_via_query(Key(User.EMAIL_ID).eq(email_id), Constants.EMAIL_INDEX) is not None:
            raise Exception(response.get_custom_exception(Constants.CONFLICT, Constants.CONFLICT))

        password_base64 = Util().encode_base64(password)  # convert to base 64

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

        users = user_table.get_item_by_key({User.USER_ID: user_id})
        user_image_url = Constants.DEFAULT_STRING
        cover_url = Constants.DEFAULT_STRING
        notification_blocked = Constants.BLOCKED
        created_at = Util().get_current_time_utc()
        contact_no = None
        device_count = None
        device_web_count = 0
        parent_user = "N/A"

        if users is not None:
            device_state = Table(DeviceState.DEVICE_STATE).get_via_query(Key(User.USER_ID).eq(user_id), Constants.USER_ID_INDEX)
            if device_state["Count"] > 0:
                device_state_list = device_state['Items']
                device_web_count = len(
                    filter(lambda device: device['appliance_id'][0]['applianceType'] == 'AC', device_state_list))

            installations = Table(Installations.INSTALLATIONS_TABLE).get_item_by_key({User.USER_ID: user_id, Installations.MOBILE_DEVICE_ID: mobile_device_id})

            if installations is not None:
                notification_blocked = int(installations[Installations.NOTIFICATION_BLOCKED])

            user_image_url = users.get(User.USER_IMAGE_URL, None)
            cover_url = users.get(User.USER_COVER_URL, None)

            if User.CURRENCY_SYMBOL in users:
                currency_symbol = users[User.CURRENCY_SYMBOL]
                cur_sym_orientation = users[User.CURRENT_SYSTEM_ORIENTATION]
                unit_price = users[User.UNIT_PRICE]
                currency_index = users[User.DEV_CURRENCY_INDEX]

            if User.USER_LEVEL in users:
                parent_user = users[User.PARENT_USER]
                user_level_index = users[User.USER_LEVEL_INDEX]
            if User.IS_DEFAULT in users:
                is_default = users[User.IS_DEFAULT]

            created_at = users[User.CREATED_AT]
            is_email_verified = users[User.IS_EMAIL_VERIFIED]
            contact_no = users[User.CONTACT_NO]
            device_count = device_state["Count"]

        else:

            user_table.put_item(
                {
                    User.USER_ID: user_id,
                    User.EMAIL_ID: email_id,
                    User.PASSWORD: password_base64,
                    User.IS_SOCIAL_MEDIA: 1,
                    User.IS_EMAIL_VERIFIED: is_email_verified,
                    User.CREATED_AT: created_at,
                    User.CONTACT_NO: contact_no,
                    User.USER_IMAGE_PATH: user_image_url,
                    User.CURRENCY_SYMBOL: currency_symbol,
                    User.CURRENT_SYSTEM_ORIENTATION: cur_sym_orientation,
                    User.UNIT_PRICE: unit_price,
                    User.DEV_CURRENCY_INDEX: currency_index,
                    User.USER_LEVEL: user_level_index,
                    User.PARENT_USER: parent_user,
                    User.IS_DELETED: Constants.DEFAULT_INT,
                    User.IS_DEFAULT: is_default
                }
            )

        response_object = {
            User.USER_ID: user_id,
            User.EMAIL_ID: email_id,
            User.CREATED_AT: created_at,
            User.IS_EMAIL_VERIFIED: is_email_verified,
            User.CONTACT_NO: contact_no,
            User.USER_IMAGE_URL: user_image_url,
            User.USER_COVER_URL: cover_url,
            DeviceState.DEVICE_COUNT: device_count,
            DeviceState.DEVICE_WEB_COUNT: device_web_count,
            Installations.NOTIFICATION_BLOCKED: notification_blocked,
            User.CURRENCY_SYMBOL: currency_symbol,
            User.CURRENT_SYSTEM_ORIENTATION: str(cur_sym_orientation),
            User.UNIT_PRICE: unit_price,
            User.DEV_CURRENCY_INDEX: str(currency_index),
            User.USER_LEVEL_INDEX: user_level_index,
            User.PARENT_USER: parent_user,
            User.IS_DEFAULT: is_default,
            CentralSystem.IOS_VERSION: central_system[CentralSystem.IOS_VERSION],
            CentralSystem.ANDROID_VERSION_CODE: float(central_system[CentralSystem.ANDROID_VERSION_CODE]),
            CentralSystem.ANDROID_VERSION: central_system[CentralSystem.ANDROID_VERSION]
        }

        try:
            lambdaClient.invoke(FunctionName='TestInstallation', InvocationType='Event ', LogType='Tail',Payload=json.dumps(payload))
        except Exception as e:
            util.log(e)

        return response.get_response(Constants.SUCCESS, Constants.SUCCESS, response_object)
    raise Exception(response.get_custom_exception(Constants.BAD_REQUEST, Constants.INVALID_JSON_FORMAT))
