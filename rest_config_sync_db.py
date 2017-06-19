from boto3.dynamodb.conditions import Key

from imports.models.appliance_rules import ApplianceRules
from imports.models.appliance_codes import ApplianceCodes
from imports.models.central_system import CentralSystem
from imports.models.manufacturer import Manufacturer
from imports.models.appliance import Appliance
from imports.constants import Constants
from imports.defaults import Defaults
from imports.response import Response
from imports.table import Table


manufacturer_table = Table(Manufacturer.MANUFACTURE_TABLE)
appliance_table = Table(Appliance.APPLIANCE_TABLE)

"""
__author__      = Umair Ansari
__copyright__   = Copyright 2007, Cielo WiGle
__date__        = 9, May 2017
__version__     = 1.0.0
"""


def lambda_handler(event, context):
    """
    
    :param event: 
    :param context: 
    :return: 
    """
    appliance_id_list = event.get('appliance_id_list', [])
    sync_db = event.get('sync_db', 1)
    response = Response()
    if appliance_id_list:

        list_appliance_code = []
        list_appliance_rule = []
        list_manufacturer = []
        list_appliance = []
        central_system = Defaults.CENTRAL_SYSTEM[Constants.ENVIRONMENT]
        manufacturer_db_version = central_system[CentralSystem.MANUFACTURE_DB_VERSION]

        for appliance_id in appliance_id_list:

            appliance_codes = get_appliance_codes(appliance_id)
            appliance_rules = get_appliance_rules(appliance_id)

            list_appliance_code.extend(appliance_codes)
            list_appliance_rule.extend(appliance_rules)

        if not sync_db:     # if its 0
            response_object = {
                'list_appliance_codes': list_appliance_code,
                'list_appliance_rules': list_appliance_rule,
                CentralSystem.MANUFACTURE_DB_VERSION: manufacturer_db_version
            }
            return response.get_response(Constants.SUCCESS, Constants.SUCCESS, response_object)

        manufacturer_list = manufacturer_table.scan_table()
        appliance_list = appliance_table.scan_table()

        for manufacturer in manufacturer_list:
            not_supported = manufacturer.get(Manufacturer.NOT_SUPPORTED, 0)
            if not_supported:
                pass
            else:
                manufacturer_object = {
                    Manufacturer.MANUFACTURE_ID: manufacturer[Manufacturer.MANUFACTURE_ID],
                    Manufacturer.MANUFACTURE_NAME: manufacturer[Manufacturer.MANUFACTURE_NAME]
                }
                list_manufacturer.append(manufacturer_object)

        for appliance in appliance_list:
            # 28 is something related to cielo device, i am not sure exactly yet
            if appliance[Appliance.MANUFACTURE_ID] != 28:
                not_supported = appliance.get(Appliance.NOT_SUPPORTED, 0)
                if not_supported:
                    pass
                else:
                    list_appliance.append(get_appliance_object(appliance))

        response_object = {
            'list_appliance_codes': list_appliance_code,
            'list_appliance_rules': list_appliance_rule,
            CentralSystem.MANUFACTURE_DB_VERSION: manufacturer_db_version,
            'list_manufacturers': list_manufacturer,
            'list_appliances': list_appliance
        }
        return response.get_response(Constants.SUCCESS, Constants.SUCCESS, response_object)
    raise Exception(response.get_custom_exception(Constants.BAD_REQUEST, Constants.INVALID_JSON_FORMAT))


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


def get_appliance_codes(appliance_id):
    """
    
    :param appliance_id: 
    :return: 
    """
    codes_list = []
    appliance_code_table = Table(ApplianceCodes.APPLIANCE_CODE_TABLE)
    response = appliance_code_table.get_item_via_query(Key(ApplianceCodes.APPLIANCE_ID).eq(appliance_id), ApplianceCodes.APPLIANCE_ID_INDEX)
    if response is not None:
        for code in response:
            CZ1 = code.get(ApplianceCodes.CZ1, None)
            CZ2 = code.get(ApplianceCodes.CZ2, None)
            CZ3 = code.get(ApplianceCodes.CZ3, None)
            construct_base_string = code.get(ApplianceCodes.CONSTRUCTED_BASE_STRING, None)
            rule = code.get(ApplianceCodes.RULE, None)

            code_object = {
                ApplianceCodes.VALUE: code[ApplianceCodes.VALUE],
                ApplianceCodes.CODE: code[ApplianceCodes.CODE],
                ApplianceCodes.MANUFACTURE_ID: code[ApplianceCodes.MANUFACTURE_ID],
                ApplianceCodes.APPLIANCE_ID: code[ApplianceCodes.APPLIANCE_ID],
                ApplianceCodes.TYPE: code[ApplianceCodes.TYPE],
                ApplianceCodes.IS_BASESTRING: code[ApplianceCodes.IS_BASESTRING],
                ApplianceCodes.IS_RULE_BASED: code[ApplianceCodes.IS_RULE_BASED],
                ApplianceCodes.RULE: rule,
                ApplianceCodes.CZ1: CZ1,
                ApplianceCodes.CZ2: CZ2,
                ApplianceCodes.CZ3: CZ3,
                ApplianceCodes.CONSTRUCTED_BASE_STRING: construct_base_string,
            }
            codes_list.append(code_object)
    return codes_list


def get_appliance_rules(appliance_id):
    """
    
    :param appliance_id: 
    :return: 
    """
    rules_list = []
    appliance_rules_table = Table(ApplianceRules.APPLIANCE_RULES_TABLE)
    response = appliance_rules_table.get_item_via_query(Key(ApplianceRules.APPLIANCE_ID).eq(appliance_id), ApplianceRules.APPLIANCE_ID_INDEX)
    if response is not None:
        for rule in response:
            rule_object = {
                ApplianceRules.MANUFACTURE_ID: rule[ApplianceRules.MANUFACTURE_ID],
                ApplianceRules.APPLIANCE_ID: rule[ApplianceRules.APPLIANCE_ID],
                ApplianceRules.MODE: rule[ApplianceRules.MODE],
                ApplianceRules.UI_RULES: rule[ApplianceRules.UI_RULES],
                ApplianceRules.EXTRA_AC_BUTTON: rule[ApplianceRules.EXTRA_AC_BUTTON],
                ApplianceRules.MODEL_RULES: rule[ApplianceRules.MODEL_RULES]
            }
            rules_list.append(rule_object)
    return rules_list
