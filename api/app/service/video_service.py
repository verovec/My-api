import random
import datetime
import os
from os.path import join, dirname, realpath

import sys
sys.path.append("..")

from app import database

from utils.Logger import Logger
from utils.ApiResponse import ApiResponse

from model.Video import Video

logger = Logger()

class VideoService():
    
    @staticmethod
    def add_format(format: str, file: str, id: str):
        response = ApiResponse()
        video = Video.query.filter_by(ids=id).first()
        video.format = {"format":format, "file":file}
        if database.save_changes(video) is False:
            response.setMessage("An error occured while saving video's details")
        else:
            logger.info("[VideosService.updateVideo] {} updated its video".format(video.name))
            response.setMessage("Video successfuly updated")
            response.setSuccess()
        return response
