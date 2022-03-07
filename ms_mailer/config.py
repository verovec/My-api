import os


DB_NAME = os.environ.get('DB_NAME', 'mail')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')


class Config(object):
    SQLALCHEMY_DATABASE_URI = "postgresql://%s:%s@%s:%s/%s" % (DB_USER,
                                                               DB_PASSWORD,
                                                               DB_HOST,
                                                               DB_PORT,
                                                               DB_NAME)
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    DEBUG = os.environ.get('DEBUG', True)
