from imports.models.central_system import CentralSystem
from imports.constants import Constants
from imports.response import Response
from imports.defaults import Defaults

"""
__author__      = Umair Ansari
__copyright__   = Copyright 2007, Cielo WiGle
__date__        = 02, May 2017
__version__     = 1.0.0
"""


def lambda_handler(event, context):
    """

    :param event: [app_type]
    :param context: []
    :return: 200, 400

    @about :    1. validate all incoming parameters, return 400 if missing
                2. create and send back response with 200 status
    """
    # TODO : move app_type and app_Version to related constant file
    app_type = event.get("app_type", "").strip()
    response = Response()
    if app_type != "" and (app_type == Constants.IOS_APPLICATION or app_type == Constants.ANDROID_APPLICATION):
        central_system = Defaults.CENTRAL_SYSTEM[Constants.ENVIRONMENT]
        app_version = {
            Constants.IOS_APPLICATION: central_system[CentralSystem.IOS_VERSION],
            Constants.ANDROID_APPLICATION: central_system[CentralSystem.ANDROID_VERSION]
        }
        response_object = {
            CentralSystem.MANUFACTURE_DB_VERSION: central_system[CentralSystem.MANUFACTURE_DB_VERSION],
            'app_version': app_version[app_type],
        }
        return response.get_response(Constants.SUCCESS, Constants.SUCCESS, response_object)
    raise Exception(response.get_custom_exception(Constants.BAD_REQUEST, Constants.INVALID_JSON_FORMAT))
