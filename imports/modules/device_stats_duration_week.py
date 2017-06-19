from stats_management_week import StatsManagementWeek
from datetime import timedelta
import decimal

"""
__author__      = Umair Ansari
__copyright__   = Copyright 2007, Cielo WiGle
__date__        = 22, May 2017
__version__     = 1.0.0
"""


class DeviceStatsDurationWeek(StatsManagementWeek):

    def get_sorted_list(self, stats_list, time_zone):
        sorted_stat_list = []
        for stat in stats_list:

            array_index = len(sorted_stat_list) - 1

            if array_index >= 0:
                new_date = self.timestamp_to_date_add_utc(timestamp=sorted_stat_list[array_index]['stat_timestamp'],
                                                          time_zone=time_zone)
            date = self.timestamp_to_date_add_utc(timestamp=stat['stat_timestamp'], time_zone=time_zone)
            if len(sorted_stat_list) > 0:

                if new_date.date() - timedelta(days=7) < date.date():
                    try:
                        sorted_stat_list[array_index]['on_duration'] += stat['on_duration']
                    except Exception as e:
                        D = decimal.Decimal
                        sorted_stat_list[array_index]['on_duration'] = D(sorted_stat_list[array_index]['on_duration'])
                        sorted_stat_list[array_index]['on_duration'] += stat['on_duration']
                    continue  # end current iteration on stats_list, start next iteration

            stat['stat_date'] = self.timestamp_to_date_add_utc(stat["stat_timestamp"], time_zone)
            stat["stat_date"] = self.convert_dates_to_formatted_string(date=stat["stat_date"])
            sorted_stat_list.append(stat)
        return sorted_stat_list