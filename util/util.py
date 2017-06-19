import datetime, base64
import smtplib, string, random
import boto3
import re
import json
import logging
from datetime import timedelta
from boto3 import dynamodb

clientS3 = boto3.client('s3')

logger = logging.getLogger()
logger.setLevel(logging.INFO)


"""
__author__      = Umair Ansari
__copyright__   = Copyright 2007, Cielo WiGle
__date__        = 25, April 2017
__version__     = 1.0.0
"""


class Util:
    """
    
    @About: this class should contains util functions only, can contain constants that are related to this class only
    @Note: one should not import constants from Constants class
    
    """
    #   Email
    SENDER_EMIL = 'noreply@cielowigle.com'
    EMAIL_SUBJECT_REST_PASSWORD = 'Cielo Forgot Password'
    STMP_SERVER = 'smtpout.secureserver.net'
    STMP_PASSWORD = 'NoRepCielo?..?'

    EMPTY_STRING = ""

    # Error messages for custom validation
    ERROR_MESSAGES = {
        "USERNAME": "username must be at least 3 to 25 character, can contain a-zA-Z0-9._ only ._ must not appear beginning or end of string.",
        "EMAIL": "this is not a valid email address.",
        "PASSWORD": "password must be at lest 5 to 15 characters."
    }

    def get_current_time_utc(self):
        """
        :author umair
        :return: it will return current time in UTC
        """
        return str(int(round((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds(), 0)))

    def encode_base64(self, string):
        """
        author umair
        :param string: string you wants to encode
        :return: return encoded string
        """
        # return string.encode('base64')  # will work with python 2 only
        # base64.b64encode('your name'.encode('ascii'))  # will work with python 2 and 3
        return base64.b64encode(string)  # will work with python 2 and 3

    def decode_base64(self, string):
        """
        author umair
        :param string: string: string you wants to decode
        :return: return decoded string
        """
        # return string.decode('base64') # will work with python 2 only
        # base64.b64decode('your name'.encode('ascii'))  # will work with python 2 and 3
        return base64.b64decode(string)  # will work with python 2 and 3

    def send_email_forget_password(self, receiver, base_url, token, social_media, user_id):
        """
        author umair
        :param receiver: this is the email of user you wants to send email 
        :param social_media: required this variable, just for check this user is from social media or not
        :param user_id: receiver name
        :param password: receiver decoded password
        :return: return True if success or return False in case of failure 
        """

        redirect_url = base_url + 'auth/reset?id=' + token
        try:
            smtp = smtplib.SMTP(Util.STMP_SERVER)
            header = 'To:' + receiver + '\n' + 'From: ' + Util.SENDER_EMIL + '\n' + 'Subject:' + Util.EMAIL_SUBJECT_REST_PASSWORD + ' \n'
            if social_media == 1:
                message = header + '\nHi, \n\nWe received a request to reset your Cielo Home password. Please login with your social media account.\n\nThanks,Cielo Wigle Team'
            else:
                message = header + '\nHi ' +user_id+ ',\n\nWe received a request to reset your Cielo Home password.\n\nTo reset your password, click on the following link:\n\n'+redirect_url +' \n\nIf you did not forget your password, please ignore this email.\n\nThanks,Cielo Wigle Team'
            smtp.login(Util.SENDER_EMIL, Util.STMP_PASSWORD)
            smtp.sendmail(Util.SENDER_EMIL, receiver, message)

            smtp.close()
        except Exception as e:
            logger.error(e)
            return False

    def id_generator(self, size=32, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
        # TODO : ask farwa about implementation of this method and write method signatures
        """
        author umair
        :param size: 
        :param chars: 
        :return: 
        """
        return ''.join(random.choice(chars) for _ in range(size))

    def get_bucket_image_path(self, bucket_name, key):
        """
        author umair
        :param bucket_name: name of S3 bucket
        :param key: user image path
        :return: return image path if found, else will return empty string
        """
        try:
            s3_response = clientS3.get_object(Bucket=bucket_name, Key=key)
            strm = s3_response['Body']
            strm_str = strm.read()
            return Util().encode_base64(strm_str)
        except Exception as e:
            # logger.error(e)
            return Util.EMPTY_STRING

    def is_valid_email(self, email):
        """
        author umair
        :param email: is the string yu wants to verify
        :return: rue if match else False
        """
        match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email)
        if match is None:
            return False
        return True

    def is_valid_username(self, username):
        """
        author umair
        :param username: is the string yu wants to verify
        :return: rue if match else False
        """
        match = re.match('^(?=.{3,25}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$', username)
        if match is None:
            return False
        return True

    def is_valid_password(self, password):
        """
        author umair
        :param password: is the string yu wants to verify
        :return: True if match else False
        
        """
        match = re.match('^.{5,15}$', password)
        if match is None:
            return False
        return True

    def validate(self, username, email, password):
        """ 
        author umair:
        :param username: is the string yu wants to verify
        :param email: is the string yu wants to verify
        :param password: is the string yu wants to verify
        :return: None if validation pass else return validation error and list of message.
        
        """
        util = Util()
        message = {}
        if util.is_valid_username(username) is False: message.update({"username": Util.ERROR_MESSAGES["USERNAME"]})
        if util.is_valid_email(email) is False: message.update({"email": Util.ERROR_MESSAGES["EMAIL"]})
        if util.is_valid_password(password) is False: message.update({"password": Util.ERROR_MESSAGES["PASSWORD"]})

        if message:
            exception = {
                'status': 400,
                'message': message
            }
            return json.dumps(exception)
        return None

    def log(self, e):
        logger.error(e)

    def block_device_by_mac_address(self, mac_address, block_message):
        try:
            authentic_devices_table = dynamodb.Table('authentic_devices')

            response = authentic_devices_table.update_item(
                Key={'mac_address': mac_address},
                UpdateExpression="set is_blocked = :is_blocked, block_message = :block_message",
                ExpressionAttributeValues={
                    ':is_blocked': 1,
                    ':block_message': block_message
                },
                ReturnValues="UPDATED_NEW")
            if 'Attributes' in response:
                return response
            else:
                return None
        except Exception as e:
            Util().log(e)
            return None

    def convert_to_utc(self, some_time, device_time_zone_offset, device_time_zone_hour, device_time_zone_minute):
        """
        
        :param some_time: 
        :param device_time_zone_offset: 
        :param device_time_zone_hour: 
        :param device_time_zone_minute: 
        :return: 
        """
        some_time_datetime = datetime.datetime.strptime(some_time, '%H:%M')
        if device_time_zone_offset == '+':
            some_time_datetime = some_time_datetime - timedelta(hours=device_time_zone_hour,
                                                                minutes=device_time_zone_minute)
        elif device_time_zone_offset == '-':
            some_time_datetime = some_time_datetime + timedelta(hours=device_time_zone_hour,
                                                                minutes=device_time_zone_minute)

        some_utc_time = some_time_datetime.time().strftime('%H:%M')
        return some_utc_time
