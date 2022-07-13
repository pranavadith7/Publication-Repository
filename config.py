import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ADMIN_SWATCH = 'cerulean'

    # mail changes
    # MAIL_SERVER = 'smtp.gmail.com'
    # MAIL_PORT = 587
    # MAIL_USE_TLS = True
    # MAIL_USE_SSL = False
    # USE_CREDENTIALS = True
    # VALIDATE_CERTS = True

    # MAIL_SUPPRESS_SEND = False
    # MAIL_DEBUG = True
    # TESTING = False
    MAIL_SERVER ='smtp.mailtrap.io'
    MAIL_PORT = 2525
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    NOREPLY_NAME = 'no-reply@facultypublicationrepo.com'
    # end change
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FACULTIES_PER_PAGE = 12
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
