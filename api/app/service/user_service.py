import os
import re
import json
import random
import datetime
from validate_email import validate_email

import sys
sys.path.append("..")

from app import database

from utils.hash import sha256, hash_id
from utils.Logger import Logger
from utils.ApiResponse import ApiResponse
from utils.utils import handleLimits

from model.User import User
from model.Video import Video
from model.JWToken import JWToken

logger = Logger()

class UserService():

    authorized_updates = [
        "username",
        "pseudo",
        "email",
        "password"
    ]
    
    @staticmethod
    def createUser(user_data):
        """
        Creates a user in the database.
        """
        response = ApiResponse()
        user = User.query.filter(
            (User.username == user_data["username"])
            | (User.pseudo == user_data["pseudo"])
            | (User.email == user_data["email"])
        ).first()
        if not user:
            username_validity = re.search("[a-zA-Z0-9_-]+", user_data["username"])
            if username_validity is not None and validate_email(user_data["email"]):
                sql_datetime = datetime.datetime.utcnow()
                user = User(
                    ids=sha256(hash_id(random.randint(1, 9999)) + user_data["username"]),
                    email=user_data["email"],
                    username=user_data["username"],
                    pseudo=user_data["pseudo"],
                    password=sha256(user_data["password"]),
                    created_at=sql_datetime,
                    updated_at=sql_datetime
                )
                if database.save_changes(user) is False:
                    response.setMessage("An error occured while persisting data to the database")
                else:
                    response.setSuccess()
                    response.setMessage("Successfuly created user")
            else:
                response.setMessage("Please enter valid details")
        else:
            response.setMessage("User already exist in the database with this pseudo, username or email")
        return response
    
    @staticmethod
    def getUserByToken(jwtoken: JWToken):
        user = User.query.filter_by(id=jwtoken.user_id).first()
        return user
            
    @staticmethod
    def getProfile(user: User):
        response = ApiResponse()
        if user is not None:
            response.setSuccess()
            response.setMessage("Details of {} found".format(user.username))
            response.setDetails({
                "id": user.ids,
                "email": user.email,
                "username": user.username,
                "pseudo": user.pseudo,
                "created_at": user.created_at
            })
        else:
            response.setMessage("Impossible to find the profile")
        return response
            
    @staticmethod
    def getProfileByIds(user_requesting: User, user_ids: str):
        user = User.query.filter_by(ids=user_ids).first()
        response = UserService.getProfile(user)
        if "email" in response.details:
            if user_requesting.ids != user_ids:
                del response.details["email"]
        else:
            response.setMessage("Profile can't be retrieved for this user")
        return response

    @staticmethod
    def updateUser(user: User, updates: dict):
        response = ApiResponse()
        if user is not None:
            perform_update = False
            for parameter in updates:
                if parameter in UserService.authorized_updates:
                    if getattr(user, parameter) != updates[parameter]:
                        perform_update = True
                        if parameter == "password":
                            setattr(user, parameter, sha256(updates[parameter]))
                        else:
                            setattr(user, parameter, updates[parameter])
            if perform_update:
                user.updated_at = datetime.datetime.utcnow()
                if database.save_changes(user) is False:
                    response.setMessage("An error occured while saving user's details")
                else:
                    logger.info("[UserService.updateUser] {} updated its profile".format(user.username))
                    response.setMessage("Profile successfuly updated")
                    response.setSuccess()
            if len(response.message) == 0:
                response.setMessage("Nothing was updated")
                response.setSuccess()
        else:
            response.setMessage("Impossible to find your profile")
        return response

    @staticmethod
    def updateUserByIds(user_requesting: User, user_ids: str, updates: dict):
        response = ApiResponse()
        user = User.query.filter_by(ids=user_ids).first()
        if user is not None:
            if user_requesting.ids == user_ids:
                return UserService.updateUser(user, updates)
            else:
                response.setMessage("You are not authorized to update this user")
        else:
            response.setMessage("Impossible to find this profile")
        return response

    @staticmethod
    def deleteUser(user: User):
        response = ApiResponse()
        if user is not None:
            if database.delete(user) is False:
                response.setMessage("An error occured while deleting this user")
            else:
                logger.info("[UserService.deleteUser] {} was deleted".format(user.username))
                response.setMessage("User successfuly deleted")
                response.setSuccess()
        else:
            response.setMessage("Impossible to find this profile")
        return response

    @staticmethod
    def deleteUserByIds(user_requesting: User, user_ids: str):
        response = ApiResponse()
        user = User.query.filter_by(ids=user_ids).first()
        if user is not None:
            if user_requesting.ids == user_ids:
                return UserService.deleteUser(user)
            else:
                response.setMessage("You are not authorized to delete this user")
        else:
            response.setMessage("Impossible to find this profile")
        return response

    @staticmethod
    def getLastUserID():
        last_user_query = User.query.order_by(User.created_at).first()
        if last_user_query is None:
            return 0
        else:
            return last_user_query.id

    @staticmethod
    def getVideoByUserID(ids: str, interval: int, page: int):
        response = ApiResponse()
        limits_response = handleLimits(Video, page, interval)
        if limits_response.error == False:
            page = limits_response.details["page"]
            interval = limits_response.details["interval"]
            offset = page * interval - interval
            videos = Video.query.filter_by(user_ids=ids).order_by(Video.name.desc()).limit(interval).offset(offset).all()
            if len(videos) >= 1:
                response.setSuccess()
                response.setMessage("{} Video found".format(len(videos)))
                data = list()
                for video in videos:
                    data.append({
                        "id": video.ids,
                        "name": video.name,
                        "description": video.description,
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
                response.setMessage("Impossible to find any video for this user")
        else:
            response = limits_response
        return response

