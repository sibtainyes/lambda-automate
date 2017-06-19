import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


"""
__author__      = Umair Ansari
__copyright__   = Copyright 2007, Cielo WiGle
__date__        = 25, April 2017
__version__     = 1.0.0"""


class Response:
    def __init__(self):
        self.code = {
            "SUCCESS": 200,
            "BAD_REQUEST": 400,
            "UNAUTHORIZED": 401,
            "FORBIDDEN": 403,
            "NOT_FOUND": 404,
            "CONFLICT": 409,
            "PRECONDITION_FAILED": 412,
            "TOO_MANY_REQUESTS": 429,
            "SERVER_ERROR": 500,
            "BAD_GATEWAY": 502,
            "SERVICE_UNAVAILABLE": 503,
            "GATEWAY_TIMEOUT": 504,
            "EMAIL_ALREADY_EXISTS": 409,
            "USERNAME_ALREADY_EXISTS": 409
        }
        self.message = {
            "SUCCESS": 'success',
            "BAD_REQUEST": 'bad request',
            "UNAUTHORIZED": 'unauthorized',
            "FORBIDDEN": 'forbidden',
            "CONFLICT": 'conflict',
            "NOT_FOUND": 'not found',
            "SERVER_ERROR": 'internal server error',
            "USERNAME_PASSWORD_MISMATCH": 'invalid username or password',
            "INVALID_JSON_FORMAT": 'invalid json format',
            "BAD_GATEWAY": 'bad gateway',
            "GATEWAY_TIMEOUT": 'gateway timeout',
            "TOO_MANY_REQUESTS": 'too many requests',
            "SERVICE_UNAVAILABLE": 'service unavailable',
            "EMAIL_ALREADY_EXISTS": 'email already exists',
            "USERNAME_ALREADY_EXISTS": 'user id already exists',
            "PASSWORD_AND_CONFIRM_PASSWORD_NOT_SAME": 'new password and confirm new password are not same',
            "PASSWORD_AND_NEW_PASSWORD_CANT_NOT_BE_SAME": 'password and new password can not be same',
            "PRECONDITION_FAILED": 'Precondition Failed'
        }

    def get_response_code(self, key):
        """
        @author: umair
        :param key: code key
        :return: code against key 
        """
        return self.code[key]

    def get_response_message(self, key):
        """
        @author: umair
        :param key: message key
        :return: message against key
        """
        return self.message[key] if self.message.has_key(key) else key

    def get_response(self, code, message, data=None):
        """
        @author: umair
        :param code: code key
        :param message: message key 
        :param data: response object
        :return: a custom response as a string
        """

        if data is not None:
            data = Response().dict_to_camel_case(data)
        return {
            'status': self.get_response_code(code),
            'message': self.get_response_message(message),
            'data': data
        }

    def get_custom_exception(self, code, message, stack_trace=None):
        """
        @author: umair
        :param code: code key
        :param message: message key
        :param stack_trace: stack_trace
        :return: a custom exception as a string
        """
        exception = {
            'status': self.get_response_code(code),
            'message': self.get_response_message(message)
        }
        if stack_trace is not None:
            logger.error(str(stack_trace))

        return json.dumps(exception)

    def dict_to_camel_case(self, data):
        """
        @author: umair
        :param data: 
        :return: 
        """
        response = Response()
        if isinstance(data, dict):
            for key, value in data.iteritems():
                del data[key]
                if isinstance(value, dict) or isinstance(value, list):
                    value = response.dict_to_camel_case(value)
                data[response.to_camel_case(key)] = value
            return data
        if isinstance(data, list):
            for i, value in enumerate(data):
                data[i] = response.dict_to_camel_case(value)
            return data

    def to_camel_case(self, snake_str):
        """
        @author: umair
        :param snake_str:  string you wants to convert into camel case
        :return: camel case formatted string
        """
        components = snake_str.split('_')
        return components[0] + "".join(x.title() for x in components[1:])
