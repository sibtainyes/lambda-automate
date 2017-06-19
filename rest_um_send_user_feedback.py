import json

from imports.models.feedback import Feedback
from imports.constants import Constants
from imports.response import Response
from imports.table import Table
from util.util import Util

"""
__author__      = Umair Ansari
__copyright__   = Copyright 2007, Cielo WiGle
__date__        = 25, April 2017
__version__     = 1.0.0
"""


def lambda_handler(event, context):
    """
    
    :param event: [user_id, email_id, application_version, application_type, message]
    :param context: [] 
    :return:  200 for success, 400 for missing parameter values
    """
    user_id = event.get(Feedback.USER_ID, "").strip()
    email_id = event.get(Feedback.EMAIL_ID, "").strip()
    application_version = event.get(Feedback.APPLICATION_VERSION, "").strip()
    application_type = event.get(Feedback.APPLICATION_TYPE, "").strip()
    message = event.get(Feedback.MESSAGE, "").strip()

    response = Response()
    feedback_table = Table(Feedback.FEEDBACK_TABLE)

    if feedback_table.get_table_object() is None:
        raise Exception(response.get_custom_exception(Constants.SERVER_ERROR, Constants.SERVER_ERROR))

    if user_id != "" and email_id != "" and application_version != "" and application_type != "" and message != "":
        exception = feedback_table.put_item({
            Feedback.FEEDBACK_ID: Util().id_generator(),
            Feedback.USER_ID: user_id,
            Feedback.EMAIL_ID: email_id,
            Feedback.APPLICATION_VERSION: application_version,
            Feedback.APPLICATION_TYPE: application_type,
            Feedback.MESSAGE: message,
            Feedback.CREATED_AT: int(Util().get_current_time_utc())
        })
        if exception is None:
            return response.get_response(Constants.SUCCESS, Constants.SUCCESS)
        raise Exception(response.get_custom_exception(Constants.SERVER_ERROR, Constants.SERVER_ERROR))
    raise Exception(response.get_custom_exception(Constants.BAD_REQUEST, Constants.INVALID_JSON_FORMAT))
