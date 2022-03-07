import datetime

from sqlalchemy import func

import sys
sys.path.append("..")

from app import database

db = database.getDatabase()

class User(db.Model):
    __tablename__ = 'User'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ids = db.Column(db.String(64), unique=True, nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    pseudo = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now())
    
    def __repr__(self):
        return "<User(username='{}', email='{}', ids='{}')>".format(
            self.username, 
            self.email, 
            self.ids
        )