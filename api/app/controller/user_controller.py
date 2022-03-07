from flask import request, escape
from flask_restplus import Resource, Namespace, fields

import sys
sys.path.append("..")

from service.user_service import UserService
from service.auth_service import AuthService, requires_authentication

from utils.ApiResponse import ApiResponse

api = Namespace('User', description='User-related operations')

user_profile_response_dto = api.model('user_profile_response', {
    'error': fields.Boolean(description="True on error, false on success"),
    'message': fields.String(description="Some error or success message"),
    'data': fields.Nested(
        api.model('user_profile_response_details', {
            'id': fields.String,
            'email': fields.String,
            'username': fields.String,
            'pseudo': fields.String,
            'created_at': fields.DateTime
        }), skip_none=True
    )
})

register_user_response_dto = api.model('register_user_response', {
    'error': fields.Boolean(description="True on error, false on success"),
    'message': fields.String(description="Some error or success message")
})

user_video_response_dto = api.model('user_video_response_details', {
    'error': fields.Boolean(description="True on error, false on success"),
    'message': fields.String(description="Some error or success message"),
    'data': fields.Nested(
        api.model('user_video_response_details', {
            'id': fields.String,
            'name': fields.String,
            'description': fields.String,
            'filename': fields.String,
            'user_id': fields.String,
            'created_at': fields.DateTime
        }), skip_none=True
    )
})

register_user_dto = api.model('register_user', {
    'username': fields.String(required=True, description='Username'),
    'pseudo': fields.String(required=True, description='Pseudo, yeah that\'s the same than the username... #LeSerieuxDeL\'ETNA'),
    'email': fields.String(required=True, description='email'),
    'password': fields.String(required=True, description='Password')
})

list_video_by_user_dto = api.parser()
list_video_by_user_dto.add_argument('page', help="The offset of the results. Used for pagination. Default is 1.")
list_video_by_user_dto.add_argument('per_page', help="The size of one row of results. Used for pagination. Default is 5.")

header_token_dto = api.parser()
header_token_dto.add_argument(
    'X-Api-Auth-Token', 
    help="JWT", 
    required=True, 
    location='headers'
)

@api.route(
    '', 
    doc={"description": "Performs user creation or update"}
)
@api.route('/<id>')
@api.doc(params={'id': 'User IDS'})
class User(Resource):

    @api.marshal_with(user_profile_response_dto, skip_none=True)
    @api.expect(header_token_dto, validate=True)
    @requires_authentication
    def get(self, id):
        token_value = escape(request.headers["X-Api-Auth-Token"])
        jwtoken = AuthService.decodeToken(token_value)
        user_requesting = UserService.getUserByToken(jwtoken)
        return UserService.getProfileByIds(user_requesting, id).getResponse()

    @api.marshal_with(register_user_response_dto, skip_none=True)
    @api.expect(register_user_dto, validate=True)
    def post(self):
        return UserService.createUser({
            "username": escape(request.json["username"]),
            "pseudo": escape(request.json["pseudo"]),
            "email": escape(request.json["email"]),
            "password": escape(request.json["password"])
        }).getResponse()

    @api.marshal_with(register_user_response_dto, skip_none=True)
    @api.expect(register_user_dto, header_token_dto, validate=True)
    @requires_authentication
    def put(self, id):
        token_value = escape(request.headers["X-Api-Auth-Token"])
        jwtoken = AuthService.decodeToken(token_value)
        user_requesting = UserService.getUserByToken(jwtoken)
        return UserService.updateUserByIds(user_requesting, id, {
            "username": escape(request.json["username"]),
            "pseudo": escape(request.json["pseudo"]),
            "email": escape(request.json["email"]),
            "password": escape(request.json["password"])
        }).getResponse()

    @api.marshal_with(register_user_response_dto, skip_none=True)
    @requires_authentication
    def delete(self, id):
        token_value = escape(request.headers["X-Api-Auth-Token"])
        jwtoken = AuthService.decodeToken(token_value)
        user_requesting = UserService.getUserByToken(jwtoken)
        return UserService.deleteUserByIds(user_requesting, id).getResponse()


@api.route('/<id>/videos')
@api.doc(params={'id': 'User IDS'})
class UserVideo(Resource):
    @api.expect(list_video_by_user_dto, validate=True)
    def get(self, id):
        page = int(request.args.get('page')) if request.args.get('page') is not None else None
        interval = int(request.args.get('per_page')) if request.args.get('per_page') is not None else None
        return UserService.getVideoByUserID(id, interval, page).getResponse()
