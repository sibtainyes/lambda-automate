import boto3

import botocore

from imports.models.central_system import CentralSystem
from imports.models.user import User
from imports.constants import Constants
from imports.defaults import Defaults
from imports.response import Response
from imports.table import Table
from util.util import Util

s3 = boto3.resource('s3')

"""
__author__      = Umair Ansari
__copyright__   = Copyright 2007, Cielo WiGle
__date__        = 25, April 2017
__version__     = 1.0.0
"""


def lambda_handler(event, context):
    """
    
    :param event: [user_id, email_id, contact_no, user_image, file_extension, image_url, image_type]
    :param context: []
    :return: 500, 200, 404, 400
    """
    # from User models
    user_id = event.get(User.USER_ID, "").strip()
    email_id = event.get(User.EMAIL_ID, "").strip()
    contact_no = event.get(User.CONTACT_NO, "").strip()

    user_image = event.get('user_image', "").strip()
    file_extension = event.get('file_extension', "").strip()
    image_url = event.get('image_url', "").strip()
    image_type = event.get('image_type', "").strip()

    response = Response()

    if user_id != "" and file_extension != "":

        date = Util().get_current_time_utc()
        param_val = None
        if user_image != "" and image_url != "":

            central_sys = Defaults.CENTRAL_SYSTEM[Constants.ENVIRONMENT]
            bucket_name = central_sys[CentralSystem.BUCKET_NAME]

            try:
                s3.meta.client.head_bucket(Bucket=bucket_name)
            except botocore.exceptions.ClientError as e:
                # If a client error is thrown, then check that it was a 404 error.
                # If it was a 404 error, then the bucket does not exist.
                error_code = int(e.response['Error']['Code'])
                if error_code == 404:
                    s3.create_bucket(Bucket=bucket_name)

            bucket = s3.Bucket(bucket_name)
            bucket.put_object(Body=user_image.decode('base64'), Key=user_id + "." + file_extension)
            param_val = user_id + "." + file_extension
            UE = "SET user_image_path = :param_val , updated_at = :date"

        # TODO : email should not be update, if we are verifying user by sending email
        elif email_id != "":
            param_val = email_id
            UE = "SET email_id = :email_id , updated_at = :date"

        elif contact_no != "":
            param_val = contact_no
            UE = "SET contact_no = :contact_no , updated_at = :date"

        elif image_url != "":
            param_val = image_url
            if image_type == 0:
                UE = "SET user_image_url = :param_val , updated_at = :date"
            else:
                UE = "SET user_cover_url = :param_val , updated_at = :date"

        else:
            raise Exception(response.get_custom_exception(Constants.BAD_REQUEST, Constants.INVALID_JSON_FORMAT))

        users_table = Table(User.USER_TABLE)
        if users_table.get_table_object() is None:
            raise Exception(response.get_custom_exception(Constants.SERVER_ERROR, Constants.SERVER_ERROR))

        users = users_table.get_item_by_key({User.USER_ID: user_id})
        if users is not None:
            result = users_table.update_item_by_key(
                {User.USER_ID: user_id},
                UE,
                {
                    ':param_val': param_val,
                    ':date': date
                },
                "UPDATED_NEW")
            if result is None:
                raise Exception(response.get_custom_exception(Constants.SERVER_ERROR, Constants.SERVER_ERROR))
            return response.get_response(Constants.SUCCESS, Constants.SUCCESS)
        raise Exception(response.get_custom_exception(Constants.NOT_FOUND, Constants.NOT_FOUND))
    raise Exception(response.get_custom_exception(Constants.BAD_REQUEST, Constants.INVALID_JSON_FORMAT))