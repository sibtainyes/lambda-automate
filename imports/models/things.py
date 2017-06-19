
"""
__author__      = Umair Ansari
__copyright__   = Copyright 2007, Cielo WiGle
__date__        = 10, May 2017
__version__     = 1.0.0"""


class Things:
    def __init__(self):
        pass

    THINGS_TABLE = "things"

    # to user with following dictionary only
    KEY_PAIR = "key_pair"
    PRIVATE_KEY = "PRIVATE_KEY"
    PUBLIC_KEY = "PUBLIC_KEY"

    KEY_PAIR_DICT = {
        "PRIVATE_KEY": "PrivateKey",
        "PUBLIC_KEY": "PublicKey"
    }

    PUB_CERTIFICATE_ARN = "pub_certificate_arn"
    THING_MAC_ADDRESS = "thing_macaddress"
    CERTIFICATE_PEM = "certificate_pem"
    CERTIFICATE_ARN = "certificate_arn"
    CERTIFICATE_ID = "certificate_id"
    IS_REGISTERED = "is_registered"
    DEVICE_TYPE = "device_type"
    THINGS_ARN = "thing_arn"
    DEVICE_ID = "device_id"
    USER_ID = "user_id"
