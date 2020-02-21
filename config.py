import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config():
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'this-is-a-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False # See chapter 4 for explanation