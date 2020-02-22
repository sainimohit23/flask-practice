from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from hashlib import md5 # for avatars

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    passowrd_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default = datetime.utcnow) # Passing the function, not calling it
    

    posts = db.relationship('Post', backref='author', lazy='dynamic')
    
    def set_password(self, password):
        self.passowrd_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.passowrd_hash, password)

    def avatar(self, size): # see chapter 6
        digest = md5(self.email.lower().encode('utf-8')).hexdigest() # expects characters in lower case and in byte form.
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size) # s for size. d is to get default avatar, 'identicon' is the name of avatar

    def __repr__(self):
        """
            __repr__ functions returns the printable representations of the objects.
            Just print the instance of object to see this in action.
        """
        return '<User {}>'.format(self.username) # for debugging purposes


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


# Because Flask-Login knows nothing about databases, it needs the application's help in loading a user.
# For that reason, the extension expects that the application will configure a user loader function, 
# that can be called to load a user given the ID.
@login.user_loader
def load_user(id):
    return User.query.get(int(id))