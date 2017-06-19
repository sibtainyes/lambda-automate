from imports.modules.custom_date import CustomDate
from boto3.dynamodb.conditions import Key, Attr
from abc import ABCMeta, abstractmethod
import boto3

dynamo_db = boto3.resource('dynamodb')

"""
__author__      = Umair Ansari
__copyright__   = Copyright 2007, Cielo WiGle
__date__        = 22, May 2017
__version__     = 1.0.0
"""


class StatsManagement(object):
    """
    A class that has a metaclass derived from ABCMeta cannot be instantiated unless all of its abstract methods are 
    1overridden"""
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, table_name, days):
        self.table = dynamo_db.Table(table_name)
        self.days = days

    @abstractmethod
    def get_sorted_list(self, list_to_sort, time_zone):
        pass

    @abstractmethod
    def get_fixed_date(self, date):
        pass

    def remove_uct_convert_to_timestamp(self, date, time_zone):
        return CustomDate().date_to_timestamp_utc_0(date=date, time_zone=time_zone)

    def timestamp_to_date_add_utc(self, timestamp, time_zone):
        return CustomDate().timestamp_to_date_add_utc(timestamp, time_zone)

    def get_database_object(self, appliance_id, device_id, end_timestamp, start_timestamp):
        _ExclusiveStartKey = {
            'device_id': str(device_id),
            'stat_timestamp': int(end_timestamp)
        }
        pe = 'device_id, appliance_id,stat_timestamp, stat_date, on_duration, avg_temp'
        ke = Key('device_id').eq(device_id)
        ke = ke & Key('stat_timestamp').gte(start_timestamp)
        fe = Attr('appliance_id').eq(appliance_id)
        stats_return = self.table.query(KeyConditionExpression=ke,
                                        FilterExpression=fe,
                                        ScanIndexForward=False,
                                        ProjectionExpression=pe,
                                        ExclusiveStartKey=_ExclusiveStartKey)
        return stats_return.get("Items", None) if stats_return['Count'] > 0 else None

    @abstractmethod
    def convert_dates_to_formatted_string(self, date, time_zone):
        pass

    def set_days(self, days):
        try:
            self.days = days
        except Exception as e:
            print (e)

    def get_days(self):
        return self.days
