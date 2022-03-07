from flask import request, escape
from flask_restplus import Resource, Namespace, fields

import sys
sys.path.append("..")

from service.videos_service import VideosService
from service.user_service import UserService
from service.auth_service import AuthService, requires_authentication

from utils.ApiResponse import ApiResponse

import werkzeug

api = Namespace('Videos', description='Listing videos operations')

video_response_dto = api.model('video_response', {
    'error': fields.Boolean(description="True on error, false on success"),
    'message': fields.String(description="Some error or success message")
})

video_model_dto = api.parser()
video_model_dto.add_argument('file', help="Video file", type=werkzeug.datastructures.FileStorage, location='files', required=True)
video_model_dto.add_argument('name', help="Name of video", required=True)
video_model_dto.add_argument('description', help="Descrition of video")
video_model_dto.add_argument('X-Api-Auth-Token', help="JWT", required=True, location='headers')

video_put_model_dto = api.parser()
video_put_model_dto.add_argument('ids', help="ids of video", required=True)
video_put_model_dto.add_argument('name', help="Name of video", required=True)
video_put_model_dto.add_argument('description', help="Descrition of video")
video_put_model_dto.add_argument('X-Api-Auth-Token', help="JWT", required=True, location='headers')

video_delete_model_dto = api.parser()
video_delete_model_dto.add_argument('ids', help="Video ids")
video_delete_model_dto.add_argument('X-Api-Auth-Token', help="JWT", required=True, location='headers')

video_get_model_dto = api.parser()
video_get_model_dto.add_argument('page', help="Page")
video_get_model_dto.add_argument('per_page', help="Number of elem by page")
video_get_model_dto.add_argument('name', help="Video name")
video_get_model_dto.add_argument('user', help="User's videos")
video_get_model_dto.add_argument('duration', help="Video duration")

video_get_by_name_model_dto = api.parser()
video_get_by_name_model_dto.add_argument('page', help="Page")
video_get_by_name_model_dto.add_argument('per_page', help="Number of elem by page")

video_get_comment_dto = api.parser()
video_get_comment_dto.add_argument('X-Api-Auth-Token', help="JWT", required=True, location='headers')
video_get_comment_dto.add_argument('page', help="Page")
video_get_comment_dto.add_argument('per_page', help="Number of elem by page")

video_post_comment_dto = api.parser()
video_post_comment_dto.add_argument('content', help="Content of comment")
video_post_comment_dto.add_argument('X-Api-Auth-Token', help="JWT", required=True, location='headers')


@api.route(
    '', 
    doc={"description": "Performs video creation or update"}
)

class Videos(Resource):
    @api.expect(video_get_model_dto, validate=True)
    def get(self):
        page = int(request.args.get('page')) if request.args.get('page') is not None else None
        interval = int(request.args.get('per_page')) if request.args.get('per_page') is not None else None
        data = dict()
        data['user'] = request.args.get('user') if request.args.get('user') is not None else None
        data['duration'] = request.args.get('duration') if request.args.get('duration') is not None else None
        data['name'] = request.args.get('name') if request.args.get('name') is not None else None
        return VideosService.listVideos(page, interval, data).getResponse()

    @api.expect(video_model_dto, validate=True)
    def post(self):
        token_value = escape(request.headers["X-Api-Auth-Token"])
        jwtoken = AuthService.decodeToken(token_value)
        user_requesting = UserService.getUserByToken(jwtoken)
        return VideosService.createVideo({
            "file": request.files["file"],
            "name": escape(request.values['name']),
            "description": escape(request.args.get('description') if request.args.get('description') is not None else None),
            "filename": escape(request.files["file"].filename),
            "user_ids": escape(user_requesting.ids)
        }).getResponse()

    @api.expect(video_put_model_dto, validate=True)
    def put(self):
        token_value = escape(request.headers["X-Api-Auth-Token"])
        jwtoken = AuthService.decodeToken(token_value)
        user_requesting = UserService.getUserByToken(jwtoken)
        data = dict()
        data['name'] = request.args.get('name') if request.args.get('name') is not None else None
        data['description'] = request.args.get('description') if request.args.get('description') is not None else None
        return VideosService.updateVideoByIds(user_requesting, request.args.get('ids'), {
            "name": data['name'],
            "description": data['description']
        }).getResponse()

    @api.expect(video_delete_model_dto, validate=True)
    def delete(self):
        token_value = escape(request.headers["X-Api-Auth-Token"])
        jwtoken = AuthService.decodeToken(token_value)
        user_requesting = UserService.getUserByToken(jwtoken)
        return VideosService.deleteVideoByID(user_requesting, request.args.get('ids')).getResponse()

@api.route('/<name>')
@api.doc(params={'name': 'Video name'})
class Video(Resource):
    @api.expect(video_get_by_name_model_dto, validate=True)
    def get(self, name):
        page = int(request.args.get('page')) if request.args.get('page') is not None else None
        interval = int(request.args.get('per_page')) if request.args.get('per_page') is not None else None
        return VideosService.getVideoByName(name, interval, page).getResponse()


@api.route('/<id>/comment')
@api.doc(params={'id': 'Video ids'})
class Video(Resource):
    @api.expect(video_get_comment_dto, validate=True)
    def get(self, id):
        token_value = escape(request.headers["X-Api-Auth-Token"])
        jwtoken = AuthService.decodeToken(token_value)
        user_requesting = UserService.getUserByToken(jwtoken)
        page = int(request.args.get('page')) if request.args.get('page') is not None else None
        interval = int(request.args.get('per_page')) if request.args.get('per_page') is not None else None
        return VideosService.getCommentByVideoID(id, interval, page).getResponse()

    @api.expect(video_post_comment_dto, validate=True)
    def post(self, id):
        token_value = escape(request.headers["X-Api-Auth-Token"])
        jwtoken = AuthService.decodeToken(token_value)
        user_requesting = UserService.getUserByToken(jwtoken)
        comment_data = {
            "content": request.args.get('content'),
            "user_ids": user_requesting.ids,
            "video_ids": id
        }
        return VideosService.addCommentByVideoID(user_requesting, comment_data).getResponse()

