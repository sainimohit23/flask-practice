import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config():
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'this-is-a-key' # used by flaskWTF to prevent cross site request forgery attacks
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db') # See chapter 4 for explanation
    SQLALCHEMY_TRACK_MODIFICATIONS = False # See chapter 4 for explanation
    POSTS_PER_PAGE = 3