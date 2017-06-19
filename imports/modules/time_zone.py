"""
__author__      = Umair Ansari
__copyright__   = Copyright 2007, Cielo WiGle
__date__        = 22, May 2017
__version__     = 1.0.0
"""


class TimeZone:
    def __init__(self):
        self.operation = None
        self.hour = None
        self.minute = None

    def set_time_zone(self, time_zone_sting):
        try:
            self.operation = time_zone_sting[0]
            app_zone = time_zone_sting[1:]
            app_zone = app_zone.split(':')
            self.hour = int(app_zone[0])
            self.minute = int(app_zone[1])
            return True
        except Exception as e:
            return False

    def get_operator(self):
        return self.operation

    def get_hour(self):
        return self.hour

    def get_minute(self):
        return self.minute
