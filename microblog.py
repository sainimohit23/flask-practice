from app import app, db
from app.models import User, Post

@app.shell_context_processor # Imports the following in flask shell automatically
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}