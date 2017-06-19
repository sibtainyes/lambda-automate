from imports.modules.device_metering_data_cost_hour import DeviceMeteringDataCostHour
from imports.modules.device_metering_data_cost_week import DeviceMeteringDataCostWeek
from imports.modules.device_metering_data_cost_day import DeviceMeteringDataCostDay
from imports.modules.device_stats_temperature_hour import DeviceStatsTemperatureHour
from imports.modules.device_stats_temperature_week import DeviceStatsTemperatureWeek
from imports.modules.device_stats_temperature_day import DeviceStatsTemperatureDay
from imports.modules.device_stats_duration_hour import DeviceStatsDurationHour
from imports.modules.device_stats_duration_week import DeviceStatsDurationWeek
from imports.modules.device_stats_duration_day import DeviceStatsDurationDay
from imports.modules.custom_date import CustomDate
from imports.modules.time_zone import TimeZone
from imports.constants import Constants
from imports.response import Response

"""
__author__      = Umair Ansari
__copyright__   = Copyright 2007, Cielo WiGle
__date__        = 22, May 2017
__version__     = 1.0.0
"""


def lambda_handler(event, context):

    device_id = event.get('device_id', "")
    appliance_id = event['appliance_id']

    # user date time, must be with UTC +-
    date_time = event.get('date_time', "")

    # user time zone
    app_time_zone = event.get('app_time_zone', "")

    """
    duration_type 
    1 : data of 1 days grouped by hour
    2 : data of 1 week grouped by day
    3 : data of 1 month grouped by day
    4 : data of 3 months(Quarter of year) grouped by week
    
    Note : above all configuration are default and can be override using following
    1 : if user pass days, then for any case number of days will be override with these days, no matter the type of class
    2 : if you want to default number of days for any type, do not change class, instead pass number days in class constructor
        see 2nd index of class_list[], like I am overriding default days
    """
    duration_type = event["duration_type"]

    days = event["days"]    # if user need custom days

    response = Response()
    custom_date = CustomDate()
    one_month = 30
    stat_type = event.get('stat_type', "")

    class_list = [
        {
            "avg_temp": DeviceStatsTemperatureHour(),
            "on_duration": DeviceStatsDurationHour(),
            "unit_cost": DeviceMeteringDataCostHour()
        },
        {
            "avg_temp": DeviceStatsTemperatureDay(),
            "on_duration": DeviceStatsDurationDay(),
            "unit_cost": DeviceMeteringDataCostDay()
        },
        {
            "avg_temp": DeviceStatsTemperatureDay(days=one_month),
            "on_duration": DeviceStatsDurationDay(days=one_month),
            "unit_cost": DeviceMeteringDataCostDay(days=one_month)
        },
        {
            "avg_temp": DeviceStatsTemperatureWeek(),
            "on_duration": DeviceStatsDurationWeek(),
            "unit_cost": DeviceMeteringDataCostWeek()
        }
    ]

    if device_id != "" and isinstance(appliance_id, int) and appliance_id != 0 and stat_type != "" and app_time_zone != "":
        try:
            stats_management = class_list[duration_type-1][stat_type]
        except Exception as e:
            raise Exception(response.get_custom_exception(code=Constants.NOT_FOUND, message="invalid durationType or statType"))

        time_zone = TimeZone()
        if time_zone.set_time_zone(time_zone_sting=app_time_zone) is False:
            raise Exception(
                response.get_custom_exception(code=Constants.BAD_REQUEST, message=Constants.INVALID_JSON_FORMAT))

        # if user have send days with request, set them. Else it will be using default days set of each type of class
        if days != 0:
            stats_management.set_days(days=days)

        # remove extra hours, minutes and seconds from date
        date_time = stats_management.get_fixed_date(date=date_time)

        # set utc to 0:00
        end_timestamp = stats_management.remove_uct_convert_to_timestamp(date=date_time, time_zone=time_zone)

        # grab the starting date from ending date
        start_timestamp = custom_date.get_start_date_timestamp(end_date_timestamp=end_timestamp, days=stats_management.get_days())

        # grab state object
        stats_list = stats_management.get_database_object(appliance_id=appliance_id, device_id=device_id, end_timestamp=end_timestamp, start_timestamp=start_timestamp)
        sorted_list = []
        if stats_list is not None:
            sorted_list = stats_management.get_sorted_list(stats_list=stats_list, time_zone=time_zone)

        return response.get_response(code=Constants.SUCCESS, message=Constants.SUCCESS, data=sorted_list)
    raise Exception(response.get_custom_exception(code=Constants.BAD_REQUEST, message=Constants.INVALID_JSON_FORMAT))
