from app import db
from app.models import *
from flask_script import Command


class InitDbCommand(Command):
    def run(self):
        init_db()
        print("Database has been initialized")


def init_db():
    db.drop_all()
    db.create_all()
