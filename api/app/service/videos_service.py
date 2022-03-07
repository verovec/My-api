import random
import datetime
import os
from mutagen.mp4 import MP4
from os.path import join, dirname, realpath
from werkzeug.utils import secure_filename

import sys
sys.path.append("..")

from app import database

from utils.hash import sha256, hash_id
from utils.Logger import Logger
from utils.ApiResponse import ApiResponse
from utils.utils import handleLimits

from model.Video import Video
from model.User import User
from model.Comment import Comment
from model.JWToken import JWToken

logger = Logger()

class VideosService():

    authorized_updates = [
        "name",
        "description"
    ]

    UPLOAD_FOLDER = join(dirname(realpath(__file__)), '../uploads/')
    ALLOWED_EXTENSIONS = {'mov', 'avi', 'mp4', 'gif'}
    
    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in VideosService.ALLOWED_EXTENSIONS


    @staticmethod
    def createVideo(video_data: dict):
        """
        Creates a video in the database.
        """
        response = ApiResponse()
        sql_datetime = datetime.datetime.utcnow()
        if VideosService.allowed_file(video_data['file'].filename):
            extension = os.path.splitext(video_data['file'].filename)[1]
            filename = sha256(hash_id(random.randint(1, 9999)) + video_data["filename"]) + extension
            video_data['file'].save(os.path.join(VideosService.UPLOAD_FOLDER, secure_filename(filename)))
            video = Video(
                ids=sha256(hash_id(random.randint(1, 9999)) + video_data["filename"]),
                name=video_data['name'],
                description=video_data['description'],
                filename=filename,
                user_ids=video_data["user_ids"],
                path='/uploads/' + filename,
                duration=VideosService.get_video_duration(filename),
                created_at=sql_datetime,
                updated_at=sql_datetime
            )
            if database.save_changes(video) is False:
                response.setMessage("An error occured while persisting data to the database")
            else:
                response.setSuccess()
                response.setMessage("Successfuly created video")
        else:
            response.setMessage("Can't upload this file")
        return response


    @staticmethod
    def getVideoFromName(name: str, interval: int, page: int):
        """
        Get a video in the database.
        """
        response = ApiResponse()
        limits_response = handleLimits(Video, page, interval)
        if limits_response.error == False:
            page = limits_response.details["page"]
            interval = limits_response.details["interval"]
            offset = page * interval - interval
            videos = Video.query.filter_by(name=name).order_by(Video.name.desc()).limit(interval).offset(offset).all()
            if len(videos) >= 1:
                response.setSuccess()
                response.setMessage("{} Video found".format(len(videos)))
                data = list()
                for video in videos:
                    data.append({
                        "id": video.ids,
                        "name": video.name,
                        "filename": video.filename,
                        "user_id": video.user_ids,
                        "created_at": str(video.created_at)
                    })
                response.setDetails({
                    "data": data,
                    "pager": {
                        "current": page,
                        "total": limits_response.details["total_nb_pages"]
                    }
                })
            else:
                response.setMessage("Impossible to find the video")
        return response


    @staticmethod
    def listVideos(page: int, interval: int, data):
        """
        List all video in the database.
        """
        response = ApiResponse()
        limits_response = handleLimits(Video, page, interval)
        if limits_response.error == False:
            page = limits_response.details["page"]
            interval = limits_response.details["interval"]
            offset = page * interval - interval
            if data['name']:
                videos = Video.query.filter_by(name=data['name']).order_by(Video.name.desc()).limit(interval).offset(offset).all()
            else:
                if data['user']:
                    try:
                        user = User.query.filter_by(username=data['user']).first()
                        videos = Video.query.filter_by(user_ids=user.ids).order_by(Video.name.desc()).limit(interval).offset(offset).all()
                    except:
                        response.setMessage('Cannot find this user, please use username')
                        return response
                else:
                    if data['duration']:
                        videos = Video.query.filter_by(duration=data['duration']).order_by(Video.name.desc()).limit(interval).offset(offset).all()
            if len(videos) >= 1:
                response.setSuccess()
                response.setMessage("{} Video found".format(len(videos)))
                data = list()
                for video in videos:
                    data.append({
                        "id": video.ids,
                        "name": video.name,
                        "filename": video.filename,
                        "duration": video.duration,
                        "user_id": video.user_ids,
                        "created_at": str(video.created_at)
                    })
                response.setDetails({
                    "data": data,
                    "pager": {
                        "current": page,
                        "total": limits_response.details["total_nb_pages"]
                    }
                })
            else:
                response.setMessage("Impossible to find the video")
        return response


    @staticmethod
    def getVideoByName(video_name: str, interval: int, page: int):
        """
        Get a video in the database by the name field.
        """
        response = VideosService.getVideoFromName(video_name, interval, page)
        return response


    @staticmethod
    def updateVideo(video: Video, updates: dict):
        """
        Update a video in the database.
        """
        response = ApiResponse()
        if video is not None:
            perform_update = False
            for parameter in updates:
                if parameter in VideosService.authorized_updates:
                    if getattr(video, parameter) != updates[parameter] and updates[parameter] != None:
                        perform_update = True
                        setattr(video, parameter, updates[parameter])
            if perform_update:
                video.updated_at = datetime.datetime.utcnow()
                if database.save_changes(video) is False:
                    response.setMessage("An error occured while saving video's details")
                else:
                    logger.info("[VideosService.updateVideo] {} updated its video".format(video.name))
                    response.setMessage("Video successfuly updated")
                    response.setSuccess()
            if len(response.message) == 0:
                response.setMessage("Nothing was updated")
                response.setSuccess()
        else:
            response.setMessage("Impossible to find your Video")
        return response


    @staticmethod
    def updateVideoByIds(user_requesting: User, video_ids: str, updates: dict):
        """
        Update a video in the database by ids field.
        """
        response = ApiResponse()
        video = Video.query.filter_by(ids=video_ids).first()
        if video is not None:
            if video.user_ids == user_requesting.ids:
                return VideosService.updateVideo(video, updates)
            else:
                response.setMessage("You are not authorized to update this video")
        else:
            response.setMessage("Impossible to find this video")
        return response


    @staticmethod
    def deleteVideo(video: Video):
        """
        Delete a video in the database.
        """
        response = ApiResponse()
        if video is not None:
            if database.delete(video) is False:
                response.setMessage("An error occured while deleting this video")
            else:
                os.remove(os.path.join(VideosService.UPLOAD_FOLDER, video.filename))
                logger.info("[VideosService.deleteVideo] {} was deleted".format(video.name))
                response.setMessage("Video successfuly deleted")
                response.setSuccess()
        else:
            response.setMessage("Impossible to find this video")
        return response


    @staticmethod
    def deleteVideoByID(user_requesting: User, video_ids: str):
        """
        Delete a video in the database by ids field.
        """
        response = ApiResponse()
        video = Video.query.filter_by(ids=video_ids).first()
        if video is not None:
            if video.user_ids == user_requesting.ids:
                return VideosService.deleteVideo(video)
            else:
                response.setMessage("You are not authorized to delete this video")
        else:
            response.setMessage("Impossible to find this video")
        return response


    @staticmethod
    def getCommentByVideoID(video_ids: str, interval: int, page: int):
        response = ApiResponse()
        limits_response = handleLimits(Video, page, interval)
        if limits_response.error == False:
            page = limits_response.details["page"]
            interval = limits_response.details["interval"]
            offset = page * interval - interval
            comments = Comment.query.filter_by(video_ids=video_ids).order_by(Comment.content.desc()).limit(interval).offset(offset).all()
            if len(comments) != 0:
                response.setSuccess()
                response.setMessage("{} Comment found".format(len(comments)))
                data = list()
                for comment in comments:
                    data.append({
                        "user_ids": comment.user_ids,
                        "video_ids": comment.video_ids,
                        "content": comment.content,
                        "updated_at": str(comment.updated_at),
                        "created_at": str(comment.created_at)
                    })
                response.setDetails({
                    "data": data,
                    "pager": {
                        "current": page,
                        "total": limits_response.details["total_nb_pages"]
                    }
                })
            else:
                response.setMessage("Impossible to find any comment")
        return response


    @staticmethod
    def addCommentByVideoID(user_requesting: User, comment_data: dict):
        response = ApiResponse()
        sql_datetime = datetime.datetime.utcnow()
        comment = Comment(
            ids=sha256(hash_id(random.randint(1, 9999)) + comment_data["content"]),
            content=comment_data['content'],
            user_ids=comment_data['user_ids'],
            video_ids=comment_data["video_ids"],
            created_at=sql_datetime,
            updated_at=sql_datetime
        )
        if database.save_changes(comment) is False:
            response.setMessage("An error occured while persisting data to the database")
        else:
            response.setSuccess()
            response.setMessage("Successfuly created comment")
        return response


    @staticmethod
    def get_video_duration(filename):
        audio = MP4(VideosService.UPLOAD_FOLDER + filename)
        return str(round(int(audio.info.length)))
