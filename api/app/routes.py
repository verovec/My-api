import os

from flask_restplus import Api
from flask import Blueprint

from controller.home_controller import api as home_ns
from controller.auth_controller import api as auth_ns
from controller.user_controller import api as user_ns
from controller.users_controller import api as users_ns
from controller.videos_controller import api as videos_ns
from controller.video_controller import api as video_ns

blueprint = Blueprint('api', __name__)
api = Api(
    blueprint, 
    title=os.environ.get("FLASK_SERVER_NAME"), 
    description=os.environ.get("FLASK_SERVER_DESCRIPTION"),
    version='1.0'
)

# Routes

api.add_namespace(home_ns, path='/home')
api.add_namespace(auth_ns, path='/auth')
api.add_namespace(user_ns, path='/user')
api.add_namespace(users_ns, path='/users')
api.add_namespace(videos_ns, path='/videos')
api.add_namespace(video_ns, path='/video')