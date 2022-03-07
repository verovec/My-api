import datetime

from sqlalchemy import func, ForeignKey

import sys
sys.path.append("..")

from app import database

db = database.getDatabase()

class Video(db.Model):
    __tablename__ = 'Video'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ids = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(255), unique=False, nullable=False)
    description = db.Column(db.String(512), unique=False, nullable=True)
    filename = db.Column(db.String(255), unique=False, nullable=False)
    user_ids = db.Column(db.String(255), ForeignKey('User.ids'), unique=False, nullable=False)
    path = db.Column(db.String(255), unique=True, nullable=False)
    duration = db.Column(db.String(255), unique=False, nullable=False)
    format = db.Column(db.JSON, unique=False, nullable=True)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now())
    
    def __repr__(self):
        return "<Video(name='{}', ids='{}', user_ids='{}', format='{}')>".format(
            self.name,
            self.ids,
            self.user_ids,
            self.format
        )