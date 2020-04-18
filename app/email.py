from flask_mail import Message
from flask import render_template

from app import mail, app
from threading import Thread


# Asynchronous Emails:
# If you are using the simulated email server that Python provides you may not have noticed this,
#  but sending an email slows the application down considerably. All the interactions that need
# to happen when sending an email make the task slow, it usually takes a few seconds to get an email out,
#  and maybe more if the email server of the addressee is slow, or if there are multiple addressees.

# What I really want is for the send_email() function to be asynchronous. What does that mean?
# It means that when this function is called, the task of sending the email is scheduled to happen
# in the background, freeing the send_email() to return immediately so that the application
# can continue running concurrently with the email being sent.

# Python has support for running asynchronous tasks, actually in more than one way.
# The threading and multiprocessing modules can both do this. Starting a background thread for email
# being sent is much less resource intensive than starting a brand new process, so I'm going to go
# with that approach

# The send_async_email function now runs in a background thread, invoked via the Thread() class in
# the last line of send_email(). With this change, the sending of the email will run in the thread,
# and when the process completes the thread will end and clean itself up. If you have configured a real
# email server, you will definitely notice a speed improvement when you press the submit
# button on the password reset request form.

# You probably expected that only the msg argument would be sent to the thread, but as you can see in the code,
# I'm also sending the application instance. When working with threads there is an important design aspect of
# Flask that needs to be kept in mind. Flask uses contexts to avoid having to pass arguments across functions.
# I'm not going to go into a lot of detail on this, but know that there are two types of contexts,
# the application context and the request context. In most cases, these contexts are automatically managed by the
# framework, but when the application starts custom threads, contexts for those threads may need to be manually created.

# There are many extensions that require an application context to be in place to work, because that allows them
# to find the Flask application instance without it being passed as an argument. The reason many extensions need
# to know the application instance is because they have their configuration stored in the app.config object.
# This is exactly the situation with Flask-Mail. The mail.send() method needs to access the configuration values
# for the email server, and that can only be done by knowing what the application is.
# The application context that is created with the with app.app_context() call makes the application
# instance accessible via the current_app variable from Flask.


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email(
        "[Microblog] Reset Your Password",
        sender=app.config["ADMINS"][0],
        recipients=[user.email],
        text_body=render_template("email/reset_password.txt", user=user, token=token),
        html_body=render_template("email/reset_password.html", user=user, token=token),
    )
