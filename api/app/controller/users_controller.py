from flask import request, escape
from flask_restplus import Resource, Namespace, fields

import sys
sys.path.append("..")

from utils.ApiResponse import ApiResponse

from service.users_service import UsersService

api = Namespace('Users', description='Listing users operations')

list_users_response_dto = api.model('list_users_response', {
    'error': fields.Boolean(description="True on error, false on success"),
    'message': fields.String(description="Some error or success message"),
    'data': fields.Nested(
        api.model('list_users_response_details', {
            'users': fields.List(
                fields.Nested(
                    api.model('list_users_list_response_details', {
                        'id': fields.String,
                        'email': fields.String,
                        'username': fields.String,
                        'pseudo': fields.String,
                        'created_at': fields.DateTime
                    }), skip_none=True
                ), skip_none=True
            ),
            'pager': fields.Nested(
                api.model('list_users_pager_response_details', {
                    'current': fields.Integer(description="Current page from which the results are returned"),
                    'total': fields.Integer(description="Total number of pages at a step of per_page's number of results")
                }), skip_none=True
            )
        }), skip_none=True
    )
}, skip_none=True)

list_users_dto = api.parser()
list_users_dto.add_argument('pseudo', help="Pseudo query. The pseudo you are looking for.")
list_users_dto.add_argument('page', help="The offset of the results. Used for pagination. Default is 1.")
list_users_dto.add_argument('per_page', help="The size of one row of results. Used for pagination. Default is 5.")

header_token_dto = api.parser()
header_token_dto.add_argument(
    'X-Api-Auth-Token', 
    help="JWT", 
    required=True, 
    location='headers'
)

@api.route(
    '', 
    doc={"description": "Listing users"}
)
class Users(Resource):

    @api.marshal_with(list_users_response_dto, skip_none=True)
    @api.expect(list_users_dto, header_token_dto, validate=True)
    def get(self):
        pseudo_query = escape(request.args.get('pseudo')) if request.args.get('pseudo') is not None else None
        page = int(request.args.get('page')) if request.args.get('page') is not None else None
        interval = int(request.args.get('per_page')) if request.args.get('per_page') is not None else None
        return UsersService.getUserList(pseudo_query, page, interval).getResponse()
