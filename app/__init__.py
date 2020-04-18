from flask import Flask, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# With the extension initialized, a bootstrap/base.html template becomes available,
# and can be referenced from application templates with the extends clause.
# This template exports a few blocks for derived templates such as title, navbar and content.
bootstrap = Bootstrap(app)
moment = Moment(app)
babel = Babel(app) # for translation

mail = Mail(app)
login = LoginManager(app)
login.login_view = "login"  # to tell flask-login what is the view function/endpoint. Chapter 5. uSED BY @login_required to force login users.
from app import routes, models

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])