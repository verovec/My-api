import datetime

from sqlalchemy import func, ForeignKey

import sys
sys.path.append("..")

from app import database

db = database.getDatabase()

class Comment(db.Model):
    __tablename__ = 'Comment'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ids = db.Column(db.String(64), unique=True, nullable=False)
    content = db.Column(db.String(255), unique=False, nullable=False)
    user_ids = db.Column(db.String(255), ForeignKey('User.ids'), unique=False, nullable=False)
    video_ids = db.Column(db.String(255), ForeignKey('Video.ids'), unique=False, nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now())
    
    def __repr__(self):
        return "<Video(name='{}', user_ids='{}')>".format(
            self.name
        )