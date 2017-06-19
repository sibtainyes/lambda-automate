
"""
__author__      = Umair Ansari
__copyright__   = Copyright 2007, Cielo WiGle
__date__        = 25, April 2017
__version__     = 1.0.0"""


class Defaults:

    def __init__(self):
        pass

    CENTRAL_SYSTEM = {
        "DEV": {
            "android_version": "1.0.8.7",
            "android_version_code": "21",
            "android_sns_app": "GCM",
            "appliance": 168,
            "appliance_dummy": 168,
            "bucket_name": "cielousers",
            "default_cur_sym_orientation": 0,
            "default_currency_index": 216,
            "default_currency_symbol": "$",
            "default_unit_price": "0.10",
            "dummy_below_26": 145,
            "dummy_breez_controlled_acs": 100,
            "dummy_breezi_controlled_acs": 133,
            "dummy_econi_controlled_appliances": 165,
            "dummy_offline": 110,
            "dummy_online": 560,
            "dummy_total_acs": 470,
            "dummy_total_acs_offline": 58,
            "dummy_total_acs_online": 412,
            "dummy_total_appliances": 200,
            "dummy_total_appliances_offline": 52,
            "dummy_total_appliances_online": 148,
            "dummy_total_devices": 670,
            "dummy_total_lights": 0,
            "dummy_total_lights_offline": 0,
            "dummy_total_lights_online": 0,
            "ec2_ip": "23",
            "ec2_to_send_ip": "23.12.13.1",
            "global_thing_certificate_arn": "qq",
            "heartbeat_rate": "1",
            "ios_version": "2.0.5",
            "ios_sns_app": "APNS_SANDBOX",
            "manufacture_db_version": "4.2.6",
            "manufacturer": 60,
            "manufacturer_dummy": 54,
            "manufacturer_seq": 2,
            "max_fota_retries": 50,
            "profile_image_url": "https://s3.amazonaws.com/cielousers/",
            "remote_image_base_url": "https://s3.amazonaws.com/cms-user/",
            "use_dummy_tables": False
        },
        "PROD": {
            # TODO : add PROD configuration here
        }
    }
