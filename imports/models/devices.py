
"""
__author__      = Umair Ansari
__copyright__   = Copyright 2007, Cielo WiGle
__date__        = 10, May 2017
__version__     = 1.0.0"""


class Devices:

    def __init__(self):
        pass

    DEVICES_TABLE = "devices"

    # index
    USER_ID_IS_REGISTERED_INDEX = "user_id-is_registered-index"

    # to user with dto only
    APPLIANCE = "appliance"
    APPLIANCE_TYPE_LIST = "appliance_type"
    # to user with following dictionary only
    APPLIANCE_ID_LIST = "appliance_id"
    APPLIANCE_ID = "APPLIANCE_ID"
    APPLIANCE_TYPE = "APPLIANCE_TYPE"

    APPLIANCE_ID_DICT = {
        "APPLIANCE_ID": "applianceId",
        "APPLIANCE_TYPE": "applianceType"

    }
    APPLICATION_VERSION = "application_version"
    DEVICE_TYPE_VERSION = "device_type_version"
    DEVICE_COORDINATES = "device_coordinates"
    APPLICATION_TYPE = "application_type"
    DEVICE_TIME_ZONE = "device_time_zone"
    IS_ENERGY_DEVICE = "is_energy_device"
    BROADCAST_NAME = "broadcast_name"
    IS_REGISTERED = "is_registered"
    BLOCK_MESSAGE = "block_message"
    DEVICE_TYPE = "device_type"
    DEVICE_NAME = "device_name"
    MAC_ADDRESS = "mac_address"
    UPDATE_TYPE = "update_type"
    CREATED_AT = "created_at"
    IS_BLOCKED = "is_blocked"
    FW_VERSION = "fw_version"
    DEVICE_ID = "device_id"
    UPDATE_AT = "updated_at"
    WIFI_NAME = "wifi_name"
    GROUP_ID = "group_id"
    USER_ID = "user_id"
