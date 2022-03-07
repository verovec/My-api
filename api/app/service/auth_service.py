import os
import time
import datetime

from flask import request, escape
from functools import wraps

import sys
sys.path.append("..")

from service.user_service import UserService

from utils.Logger import Logger
from utils.ApiResponse import ApiResponse
from utils.hash import sha256, hash_id

from model.User import User
from model.JWToken import JWToken

logger = Logger()

def requires_authentication(f):
    """
    Middleware decorator for checking token presence
    and validity in the headers.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        response = ApiResponse()
        if "X-Api-Auth-Token" in request.headers:
            token_value = escape(request.headers["X-Api-Auth-Token"])
            response = AuthService.checkToken(token_value)
        else:
            response.setMessage("Missing token in header of the query : X-Api-Auth-Token")

        if response.error is True:
            response.setHTTPCode(401)
            return response.getResponse()
        else:
            return f(*args, **kwargs)
    return wrapper

class AuthService():

    @staticmethod
    def authUser(username: str, password: str):
        response = ApiResponse()
        user = User.query.filter_by(username=username, password=sha256(password)).first()
        if user is not None:
            jwtoken = JWToken("init", user.id)
            response.setDetails({
                "token": jwtoken.encode(),
                "expires_at": jwtoken.expires_at
            })
            response.setSuccess()
            response.message = "Authentication succeeded" 
        else:
            response.setMessage("Invalid credentials")
        return response

    @staticmethod
    def decodeToken(token_value: str):
        jwtoken = JWToken("decode", token_value)
        if jwtoken.initialized is not False:
            return jwtoken
        else:
            return False

    @staticmethod
    def checkToken(token_value: str):
        """
        Checks the expiration date of a specific token as well as
        the existance of the user attached to it.
        """
        response = ApiResponse()
        jwtoken = AuthService.decodeToken(token_value)
        if jwtoken is not False:
            user = User.query.filter_by(id=jwtoken.user_id).first()
            if (user is not None):
                expires_at_dt = datetime.datetime.fromtimestamp(jwtoken.expires_at)
                response.setSuccess()
                response.setMessage("Valid token until : " + str(expires_at_dt))
                response.setDetails({ "expires_at": jwtoken.expires_at })
            else:
                response.setMessage("User linked to this token doesn't exist anymore")
        else:
            response.setMessage("Invalid or expired token, please login")
        return response
