import math
import sys
sys.path.append("..")
from utils.ApiResponse import ApiResponse
from model.User import User
from app import database

db = database.getDatabase()

def handleLimits(model: db.Model, page: int, interval: int):
    response = ApiResponse()
    total_nb_rows = model.query.count()
    if page is None:
        page = 1
    if interval is None:
        interval = 5
    total_nb_pages = math.ceil(total_nb_rows / interval) if total_nb_rows != 0 else 0
    if total_nb_pages - page < 0:
        response.setMessage("Page number requested doesn't exist for this interval")
    if page < 1:
        response.setMessage("You set the page parameter < 1")
    if interval < 1:
        response.setMessage("You set the per_page parameter < 1")
    if len(response.message) == 0:
        response.setSuccess()
        response.setDetails({
            "page": page,
            "interval": 100 if interval > 100 else interval,
            "total_nb_pages": total_nb_pages
        })
    return response