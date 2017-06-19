
"""
__author__      = Umair Ansari
__copyright__   = Copyright 2007, Cielo WiGle
__date__        = 25, April 2017
__version__     = 1.0.0"""

class Constants:

    #   response codes constants are define below
    def __init__(self):
        pass

    ENVIRONMENT = "DEV"
    # ENVIRONMENT = "PROD"

    PASSWORD_AND_NEW_PASSWORD_CANT_NOT_BE_SAME = 'PASSWORD_AND_NEW_PASSWORD_CANT_NOT_BE_SAME'
    PASSWORD_AND_CONFIRM_PASSWORD_NOT_SAME = 'PASSWORD_AND_CONFIRM_PASSWORD_NOT_SAME'
    USERNAME_PASSWORD_MISMATCH = 'USERNAME_PASSWORD_MISMATCH'
    USERNAME_ALREADY_EXISTS = 'USERNAME_ALREADY_EXISTS'
    EMAIL_ALREADY_EXISTS = 'EMAIL_ALREADY_EXISTS'
    INVALID_JSON_FORMAT = 'INVALID_JSON_FORMAT'
    PRECONDITION_FAILED = 'PRECONDITION_FAILED'
    UNAUTHORIZED = 'UNAUTHORIZED'
    SERVER_ERROR = 'SERVER_ERROR'
    BAD_REQUEST = 'BAD_REQUEST'
    FORBIDDEN = 'FORBIDDEN'
    NOT_FOUND = 'NOT_FOUND'
    CONFLICT = 'CONFLICT'
    SUCCESS = 'SUCCESS'

    #   JSON Web Token constants are defined below
    JWT_TWO_DAYS = 'JWT_TWO_DAYS'
    JWT_ONE_WEEK = 'JWT_ONE_WEEK'
    JWT_ONE_YEAR = 'JWT_ONE_YEAR'
    JWT_ONE_DAY = 'JWT_ONE_DAY'
    JWT_SECRET = 'JWT_SECRET'
    JWT_ALGO = 'JWT_ALGO'

    TOKEN = 'token'

    #   User Roles
    CIELO_ADMIN = 'CIELO_ADMIN'
    MANUFACTURE = 'MANUFACTURE'
    DISTRIBUTOR = 'DISTRIBUTOR'
    END_USER = 'END_USER'

    #   Table Name
    INSTALLATIONS = 'installation'
    DEVICE_STATE = 'device_state'
    CENTRAL_SYS = 'central_sys'
    FEEDBACK = 'feedback'
    USER = 'users'

    #   Table Index
    '''
        issue : multiple index with same names
    '''
    PARENT_USER_IS_DELETED = 'parent_user-is_deleted-index'
    USER_ID_INDEX = 'user_id-index'
    EMAIL_INDEX = 'email_id-index'

    #   Parameters
    PASSWORD = 'password'
    USERNAME = 'username'
    EMAIL = 'email'

    #   notification
    UNBLOCKED = 0
    BLOCKED = 1  # it should not be sting, change application workflow instead

    # app type
    ANDROID_APPLICATION = "ANDROID"
    WEB_APPLICATION = 'WEB'
    IOS_APPLICATION = 'IOS'

    """
        SNS_APPLICATION
    """
    SNS_APPLICATION = {
        "IOS": 'arn:aws:sns:us-east-1:598858048125:app/APNS_SANDBOX/Cielo_iOS',
        "ANDROID": 'arn:aws:sns:us-east-1:598858048125:app/GCM/Cielo_Android'
    }

    # default
    DEFAULT_STRING = "N/A"
    DEFAULT_INT = 0

    ALL_OLD = 'ALL_OLD'

    DEFAULT_POWER_OFF_START = "17:01"
    DEFAULT_POWER_ON_START = "09:00"
    DEFAULT_POWER_OFF_END = "08:59"
    DEFAULT_POWER_ON_END = "17:00"
