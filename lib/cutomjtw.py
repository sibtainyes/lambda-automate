from datetime import datetime, timedelta
import jwt

"""
__author__      = Umair Ansari
__copyright__   = Copyright 2007, Cielo WiGle
__date__        = 10, April 2017
__version__     = 1.0.0"""


class CustomJWT:
    def __init__(self):
        self.jwt = {
            "JWT_ONE_DAY": 1,
            "JWT_TWO_DAYS": 2,
            "JWT_ONE_WEEK": 7,
            "JWT_ONE_YEAR": 365,
            "JWT_SECRET": '$3cR3t#K3y',
            "JWT_ALGO": 'HS256'
        }

    def get_custom_jwt(self, key):
        return self.jwt[key]


    def get_payload(self, user_id, expire):
        return {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=CustomJWT().get_custom_jwt(expire))
        }

    def get_payload_with_email(self, user_id, email_id,expire):
        return {
            'user_id': user_id,
            'email_id': email_id,
            'exp': datetime.utcnow() + timedelta(days=CustomJWT().get_custom_jwt(expire))
        }

    def get_token(self, user_id, duration, secret, algo):
        payload = CustomJWT().get_payload(user_id, duration)
        return jwt.encode(payload, CustomJWT().get_custom_jwt(secret), algorithm=CustomJWT().get_custom_jwt(algo))

    def get_token_with_email(self, user_id, email_id, duration, secret, algo):
        payload = CustomJWT().get_payload_with_email(user_id, email_id, duration)
        return jwt.encode(payload, CustomJWT().get_custom_jwt(secret), algorithm=CustomJWT().get_custom_jwt(algo))

    def decode_token(self, token, secret, algo):
        try:
            return jwt.decode(token, CustomJWT().get_custom_jwt(secret), algorithms=CustomJWT().get_custom_jwt(algo))
        except Exception as e:
            print (e)
            return None
