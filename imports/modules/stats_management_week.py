from imports.modules.custom_date import CustomDate
from imports.modules.stats_management import StatsManagement
from abc import ABCMeta, abstractmethod

DEVICE_STATS = "device_stats"
QUARTER_YEAR = 90
ONE_MONTH = 30
ONE_WEEK = 7
ONE_DAY = 1

"""
__author__      = Umair Ansari
__copyright__   = Copyright 2007, Cielo WiGle
__date__        = 22, May 2017
__version__     = 1.0.0
"""


class StatsManagementWeek(StatsManagement):
    __metaclass__ = ABCMeta

    def convert_dates_to_formatted_string(self, date, time_zone=None):
        date = CustomDate().remove_hour_from_date(date=date)
        return CustomDate().date_to_string(date)

    def get_fixed_date(self, date):
        return CustomDate().remove_hour_from_date_string(date=date)

    def __init__(self, days=0):
        super(StatsManagementWeek, self).__init__(table_name=DEVICE_STATS, days=QUARTER_YEAR)
        if days != 0:
            self.set_days(days=days)

    @abstractmethod
    def get_sorted_list(self, stats_list, time_zone):
       pass
