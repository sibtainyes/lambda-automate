
"""
__author__      = Umair Ansari
__copyright__   = Copyright 2007, Cielo WiGle
__date__        = 25, April 2017
__version__     = 1.0.0"""


class UserLevel:
    """
    @author: umair
    @date: 25, April 2017
    @copyRight: Cielo WiGle
    
    @about: contains user level and their names
    """
    def __init__(self):
        self.level_index = {
            "CIELO_ADMIN": 1,
            "MANUFACTURE": 2,
            "DISTRIBUTOR": 3,
            "END_USER": 4
        }
        self.level_name = {
            "CIELO_ADMIN": 'Cielo Admin',
            "MANUFACTURE": "Manufacturer",
            "DISTRIBUTOR": "Distributor",
            "END_USER": "End User"
        }

    def get_user_level_index(self, key):
        """
        @author: umair
        
        :param key: level key
        :return: level
        """
        return self.level_index[key]

    def get_user_level_name(self, key):
        """
        @author: umair
        :param key: level key
        :return: level name
        """
        return self.level_name[key]
