from datetime import datetime, timedelta
"""
__author__      = Umair Ansari
__copyright__   = Copyright 2007, Cielo WiGle
__date__        = 22, May 2017
__version__     = 1.0.0
"""

"""
    @author: umair
    @date: 21, May 2017
    @copyRight: Cielo WiGle
    
1. datetime.date(2017, 7, 1) creating custom date
2. today = datetime.date.today() today's date
    today.year , today.today, today.month
    today.weekday() Monday is 0 and Sunday is 6
    today.isoweekday() Monday is 1 and Sunday is 7
    
3.  time delta are the difference between tow days
    datetime.timedelta(days=7) we can use this to add or subtract from date
    
    if we add os subtract a timedelta from a date, we will get a date
    if we add or subtract two dates we will get time delta
    
    date2 = date1 + timedelta
    timedelta = date1 + date2
    
    timedelta.day to get simple number
    timedelta.total_seconds() to get total seconds
    
4. time = datetime.time(9, 30, 20, 2000) hour minute second millisecond

    time.hour ,  time.minute
    
    datetime.datetime access both date and time
    
5.  datetime.datetime.today() return current local datetime with timezone of none
    datetime.datetime.now() gives us the option to pass timezone, if nothing is passed it wil be set to none
    datetime.datetime.utcnow()
    
PS : always keep in mind utc when working with date n time

using pytz
6. datetime.datetime(2017, 5, 18, 10, 10, 2, tzinfo=pytz.UTC) create datetime with utc
    time = datetime.datetime.now(tz=pytz.UTC) get current UTC time
    datetime.datetime.utcnow().replace(tzinfo=pytz.UTC) get current UTC time
    
    
    time.astimezone(pytz.timezone(""))
    
7. print all pytz tiemzone

    for tz in pytz.all_timezones:
        print(tz)
        
8. adding timezone to local date
    
    datetime = datetime.datetime.now()
    timezone = pytz.timezone("")
    
    timezone.localise(datetime)
    
9. change format
    date to string
    datetime.strftime('%B %d, %Y') view of python site
    
    str = 'May 21, 2017'
    datetime.datetime.strptime(str, '%B %d, %Y') string to datetime
"""


class CustomDate:
    def __init__(self):
        pass

    def get_start_date_timestamp(self, end_date_timestamp, days):
        end_date = datetime.utcfromtimestamp(end_date_timestamp)  # convert to date with 0:00 UTC
        start_date = end_date - timedelta(days=days)    # find difference
        # convert back to timestamp
        return int((start_date.replace(tzinfo=None) - datetime(1970, 1, 1)).total_seconds())

    def convert_timestamp_to_string_date(self, date, time_zone):
        operation = time_zone.get_operator()
        hour = time_zone.get_hour()
        minute = time_zone.get_minute()

        start_date = None
        if operation == "-":
            start_date = date - timedelta(hours=hour, minutes=minute)
        else:
            start_date = date + timedelta(hours=hour, minutes=minute)

        return self.date_to_string(start_date)

    def remove_minutes_date_string(self, date):
        date = self.string_to_datetime(date_string=date)
        return self.remove_minutes_from_date(date=date)

    def remove_hour_from_date(self, date):
        return date - timedelta(days=0, hours=date.hour, minutes=date.minute, seconds=date.second, microseconds=date.microsecond)

    def date_to_string(self, date):
        # generated example date '2017-05-16 08:45:03 PM'
        return date.strftime('%Y-%m-%d %I:%M:%S %p')

    def date_to_timestamp_utc_0(self, date, time_zone):
        operation = time_zone.get_operator()
        hour = time_zone.get_hour()
        minute = time_zone.get_minute()

        start_date = None
        if operation == "-":
            start_date = date + timedelta(hours=hour, minutes=minute)
        else:
            start_date = date - timedelta(hours=hour, minutes=minute)

        return int((start_date.replace(tzinfo=None) - datetime(1970, 1, 1)).total_seconds())

    def timestamp_to_date_add_utc(self, timestamp, time_zone):
        date = datetime.utcfromtimestamp(timestamp)   # convert to date
        # operation = time_zone.get_operator()
        # hour = time_zone.get_hour()
        # minute = time_zone.get_minute()
        #
        # start_date = None
        # if operation == "-":
        #     start_date = date - timedelta(hours=hour, minutes=minute)
        # else:
        #     start_date = date + timedelta(hours=hour, minutes=minute)

        return date

    def string_to_datetime(self, date_string):
        return datetime.strptime(date_string, '%Y-%m-%d %I:%M:%S %p')

    def remove_minutes_from_date(self, date):
        return date - timedelta(days=0, hours=0, minutes=date.minute, seconds=date.second, microseconds=date.microsecond)

    def remove_hour_from_date_string(self, date):
        date = self.string_to_datetime(date_string=date)
        return self.remove_hour_from_date(date=date)

    def remove_days_from_date(self, date):
        return date - timedelta(days=date.day, hours=date.hour, minutes=date.minute, seconds=date.second, microseconds=date.microsecond)

    def remove_days_from_date_string(self, date):
        date = self.string_to_datetime(date_string=date)
        return self.remove_hour_from_date(date=date)

    def timestamp_to_date_add_utc_test(self, timestamp, time_zone):
        date = datetime.utcfromtimestamp(timestamp)   # convert to date
        operation = time_zone.get_operator()
        hour = time_zone.get_hour()
        minute = time_zone.get_minute()

        start_date = None
        if operation == "-":
            start_date = date - timedelta(hours=hour, minutes=minute)
        else:
            start_date = date + timedelta(hours=hour, minutes=minute)

        return start_date