from flask import request, escape
from flask_restplus import Resource, Namespace, fields

import sys
sys.path.append("..")

from service.video_service import VideoService
from service.user_service import UserService
from service.auth_service import AuthService, requires_authentication

from utils.ApiResponse import ApiResponse

import werkzeug

api = Namespace('Video', description='Listing video operations')

video_response_dto = api.model('video_response', {
    'error': fields.Boolean(description="True on error, false on success"),
    'message': fields.String(description="Some error or success message")
})

video_model_dto = api.parser()
video_model_dto.add_argument('file', help="Path of video", required=True)
video_model_dto.add_argument('format', help="Format of video", required=True)

@api.route('/<id>')
@api.doc(params={'id': 'Video ids'})
class Video(Resource):
    @api.expect(video_model_dto, validate=True)
    def patch(self, id):
        file = request.args.get('format')
        format = request.args.get('file')
        return VideoService.add_format(format, file, id).getResponse()
