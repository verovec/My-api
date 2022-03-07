import sys
sys.path.append("..")

from utils.Logger import Logger
from utils.ApiResponse import ApiResponse
from utils.utils import handleLimits

from model.User import User

logger = Logger()

class UsersService():

    @staticmethod
    def formatUser(user: User):
        return {
            "id": user.ids,
            "email": user.email,
            "username": user.username,
            "pseudo": user.pseudo,
            "created_at": user.created_at
        }
    
    @staticmethod
    def getUserList(pseudo_query: str, page: int, interval: int):
        response = ApiResponse()
        limits_response = handleLimits(User, page, interval)
        if limits_response.error == False:
            page = limits_response.details["page"]
            interval = limits_response.details["interval"]
            offset = page * interval - interval
            if pseudo_query is not None and len(pseudo_query) > 0:
                search = "%{}%".format(pseudo_query)
                users = User.query.filter(User.pseudo.like(search)).order_by(User.id.desc()).limit(interval).offset(offset).all()
            else:
                users = User.query.order_by(User.id.desc()).limit(interval).offset(offset).all()
            users = list(map(UsersService.formatUser, users))
            response.setDetails({
                "users": users,
                "pager": {
                    "current": page,
                    "total": limits_response.details["total_nb_pages"]
                }
            })
            response.setSuccess()
        else:
            response = limits_response
        return response
