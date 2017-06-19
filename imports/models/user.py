
"""
__author__      = Umair Ansari
__copyright__   = Copyright 2007, Cielo WiGle
__date__        = 26, April 2017
__version__     = 1.0.0"""


class User:

    def __init__(self):
        pass

    # table name
    USER_TABLE = 'users'

    # index name
    USER_EMAIL_INDEX = 'email_id-index'

    DEV_CURRENCY_INDEX = 'dev_currency_index'
    USER_LEVEL_INDEX = 'user_level_index'

    #   fields
    CURRENT_SYSTEM_ORIENTATION = 'cur_sym_orientation'
    IS_EMAIL_VERIFIED = 'is_email_verified'
    USER_IMAGE_PATH = 'user_image_path'
    IS_SOCIAL_MEDIA = 'is_social_media'
    CURRENCY_SYMBOL = 'currency_symbol'
    USER_IMAGE_URL = 'user_image_url'
    TOKEN_IS_VALID = "token_is_valid"
    USER_COVER_URL = 'user_cover_url'
    ENCODED_TOKEN = "encoded_token",
    PARENT_USER = 'parent_user'
    UPDATED_AT = 'updated_at',
    IS_DEFAULT = 'is_default'
    USER_LEVEL = 'user_level'
    IS_DELETED = 'is_deleted'
    CONTACT_NO = 'contact_no'
    CREATED_AT = 'created_at'
    UNIT_PRICE = 'unit_price'
    EMAIL_ID = 'email_id'
    PASSWORD = 'password'
    USER_ID = 'user_id'
