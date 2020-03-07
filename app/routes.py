from flask import render_template, flash, redirect
from flask import url_for
from flask import request
from flask_login import current_user, login_user
from flask_login import logout_user, login_required

from werkzeug.urls import url_parse
from datetime import datetime

from app.models import User
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm

@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {'username': 'Miguel'} # Not used after the introduction of database
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next') # after getting forced login, this is to redirect to endpoint from where login was asked.
        # the @login_required decorator will intercept the request and respond with a redirect to /login, 
        # but it will add a query string argument to this URL, making the complete redirect URL /login?next=/index.

#       There are actually three possible cases that need to be considered to determine where to redirect after a successful login:

#       If the login URL does not have a next argument, then the user is redirected to the index page.
#       If the login URL includes a next argument that is set to a relative path (or in other words, a URL without the domain portion),
#       then the user is redirected to that URL.
#       If the login URL includes a next argument that is set to a full URL that includes a domain name, then the user is redirected to the index page.

#       The first and second cases are self-explanatory. The third case is in place to make the application more secure. 
#       An attacker could insert a URL to a malicious site in the next argument, so the application only redirects when the URL is relative, 
#       which ensures that the redirect stays within the same site as the application. To determine if the URL is relative or absolute, 
#       I parse it with Werkzeug's url_parse() function and then check if the netloc component is set or not.
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user() # imported from flask_login
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login')) # url_for() function takes the endpoint name as input
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username): # argument is extracted from link variable
    # below if user found, it will return first user 
    # otherwise it will raise error 404 by itself, we don't need to do that explicitly.
    user = User.query.filter_by(username=username).first_or_404() 
    
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        # db.session.add(current_user)
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


""" --------------- Follower Routes ---------------- """
@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You have unfollowed {}'.format(username))
    return redirect(url_for('user', username=username))