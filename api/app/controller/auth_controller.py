import time
import datetime

from flask import request, escape
from flask_restplus import Resource, Namespace, fields

import sys
sys.path.append("..")

from utils.ApiResponse import ApiResponse
from utils.Logger import Logger
from utils.hash import sha256

from model.User import User

from service.auth_service import AuthService, requires_authentication

logger = Logger()

# DTOs

api = Namespace('Auth', description='Authentication-related operations')

auth_login_dto = api.model('auth_login', {
    'username': fields.String(required=True, description='LDAP uid'),
    'password': fields.String(required=True, description='LDAP password')
})

auth_login_response_dto = api.model('auth_login_response', {
    'error': fields.Boolean(description="True on error, false on success"),
    'message': fields.String(description="Some error or success message"),
    'data': fields.Nested(
        api.model('auth_login_response_details', {
            'token': fields.String,
            'expires_at': fields.Integer(description="As unix timestamp in seconds")
        }), skip_none=True
    ),
    'http_code': fields.Integer
})

auth_header_token_dto = api.parser()
auth_header_token_dto.add_argument(
    'X-Api-Auth-Token', 
    help="Token is renewed each time this header exist", 
    required=True, 
    location='headers'
)

# LDAP routes (prefixed by "/auth")

@api.route(
    '',
    doc={"description": "Login with your credentials."}
)
class AuthLogin(Resource):

    @api.marshal_with(auth_login_response_dto, skip_none=True)
    @api.expect(auth_login_dto, validate=True)
    def post(self):
        return AuthService.authUser(
            escape(request.json["username"]),
            escape(request.json["password"])
        ).getResponse()


@api.route(
    '/check',
    doc={"description": "Route for checking your token's status."}
)
class AuthCheck(Resource):

    @api.marshal_with(auth_login_response_dto, skip_none=True)
    @api.expect(auth_header_token_dto, validate=True)
    @requires_authentication
    def post(self):
        return AuthService.checkToken(escape(request.headers["X-Api-Auth-Token"])).getResponse()
