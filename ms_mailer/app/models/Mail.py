from app import db
from config import Config
import datetime
from flask_serialize import FlaskSerializeMixin
from sqlalchemy.orm import backref
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import func, ForeignKey


class Mail(db.Model, FlaskSerializeMixin):
    __tablename__ = "Mail"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ids = db.Column(db.String(64), unique=True, nullable=False)
    type = db.Column(db.String(255), unique=True, nullable=False)
    subject = db.Column(db.String(255), unique=True, nullable=False)
    content = db.Column(db.String(512), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now())
