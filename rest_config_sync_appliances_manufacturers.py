from imports.models.manufacturer import Manufacturer
from imports.models.appliance import Appliance
from imports.constants import Constants
from imports.response import Response
from imports.table import Table

manufacturer_table = Table(Manufacturer.MANUFACTURE_TABLE)
appliance_table = Table(Appliance.APPLIANCE_TABLE)

"""
__author__      = Umair Ansari
__copyright__   = Copyright 2007, Cielo WiGle
__date__        = 10, May 2017
__version__     = 1.0.0
"""


def lambda_handler(event, context):
    """
    
    :param event: 
    :param context: 
    :return: 
    """

    specific_attr = event.get('specific_attr', 0)
    response = Response()
    list_manufacturer = get_manufacturers_list()
    list_appliance = get_appliances_list(specific_attr)

    response_object = {
        'list_manufacturers': list_manufacturer,
        'list_appliances': list_appliance
    }
    return response.get_response(Constants.SUCCESS, Constants.SUCCESS, response_object)



def get_manufacturers_list():
    manufacturer_list = manufacturer_table.scan_table()
    manufacturer_object_list = []
    for manufacturer in manufacturer_list:
        manufacturer_object = {
            Manufacturer.MANUFACTURE_ID: manufacturer[Manufacturer.MANUFACTURE_ID],
            Manufacturer.MANUFACTURE_NAME: manufacturer[Manufacturer.MANUFACTURE_NAME]
        }
        manufacturer_object_list.append(manufacturer_object)
    return manufacturer_object_list


def get_appliances_list(specific_attr):
    appliance_list = appliance_table.scan_table()
    appliance_object_list = []
    appliance_object = []
    for appliance in appliance_list:
        if specific_attr:
            appliance_object = {
                Appliance.APPLIANCE_ID: appliance[Appliance.APPLIANCE_ID],
                Appliance.MODEL_NUMBER: appliance[Appliance.MODEL_NUMBER],
                Appliance.MANUFACTURE_ID: int(appliance[Appliance.MANUFACTURE_ID])
            }
        else:
            not_supported = appliance.get(Appliance.NOT_SUPPORTED, 0)
            if not_supported:
                pass
            else:
                appliance_object = (get_appliance_object(appliance))
        appliance_object_list.append(appliance_object)
    return appliance_object_list


def get_appliance_object(appliance):
    """

    :param appliance: 
    :return: 
    """
    return {
        Appliance.APPLIANCE_ID: appliance[Appliance.APPLIANCE_ID],
        Appliance.NAME: appliance[Appliance.NAME],
        Appliance.APPLIANCE_TYPE: appliance[Appliance.APPLIANCE_TYPE],
        Appliance.BASESTRING: appliance[Appliance.BASESTRING],
        Appliance.CHECKSUM: appliance[Appliance.CHECKSUM],
        Appliance.START_PATTERN: appliance[Appliance.START_PATTERN],
        Appliance.ON_TIMING: appliance[Appliance.ON_TIMING],
        Appliance.ZERO_TIMING: appliance[Appliance.ZERO_TIMING],
        Appliance.MANUFACTURE_ID: int(appliance[Appliance.MANUFACTURE_ID]),
        Appliance.TEMP: appliance[Appliance.TEMP],
        Appliance.FAN: appliance[Appliance.FAN],
        Appliance.SWING: appliance[Appliance.SWING],
        Appliance.MODE: appliance[Appliance.MODE],
        Appliance.REPEAT_DELAY: appliance[Appliance.REPEAT_DELAY],
        Appliance.REPEAT_STATUS: appliance[Appliance.REPEAT_STATUS],
        Appliance.MODEL_NUMBER: appliance[Appliance.MODEL_NUMBER],
        Appliance.BT_HIGH_THRESHOLD: appliance[Appliance.BT_HIGH_THRESHOLD],
        Appliance.BT_START_INDEX: appliance[Appliance.BT_START_INDEX],
        Appliance.BT_STRING_LENGTH: appliance[Appliance.BT_STRING_LENGTH],
        Appliance.SIGNAL_LENGTH: appliance[Appliance.SIGNAL_LENGTH],
        Appliance.IS_D2: appliance[Appliance.IS_D2],
        Appliance.IS_D1: appliance[Appliance.IS_D1],
        Appliance.HEADER_LENGTH: appliance[Appliance.HEADER_LENGTH],
        Appliance.FREQUENCY: appliance[Appliance.FREQUENCY],
        Appliance.CARRY_TYPE: appliance[Appliance.CARRY_TYPE],
        Appliance.OPERATION_TYPE: appliance[Appliance.OPERATION_TYPE],
        Appliance.MULTI_WAVE_DELAY: appliance[Appliance.MULTI_WAVE_DELAY],
        Appliance.BASE_STRING_FORMAT: appliance[Appliance.BASE_STRING_FORMAT],
        Appliance.CZ1: appliance[Appliance.CZ1],
        Appliance.CZ2: appliance[Appliance.CZ2],
        Appliance.CZ3: appliance[Appliance.CZ3],
        Appliance.CONSTRUCTED_LENGTH: appliance[Appliance.CONSTRUCTED_LENGTH],
        Appliance.PVR: appliance.get(Appliance.PVR, None),
        Appliance.IS_FAREN: appliance.get(Appliance.IS_FAREN, 0),
        Appliance.IS_POWER_IGNORED: appliance.get(Appliance.IS_POWER_IGNORED, 0)
    }


lambda_handler({},[])