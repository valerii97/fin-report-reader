from datetime import timedelta


class BaseConfig():
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'dfdfe25e45ef45e5f45f351515'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 1024 * 1024
    SECURITY_PASSWORD_SALT = 'hdfonwjansdgkn9f686dusb'
    SECURITY_REGISTERABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_SEND_REGISTER_EMAIL = False

class DevConfig(BaseConfig):
    ENV = 'development'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgres://username:password@localhost:port/databasename' #change to your data
    SECURITY_EMAIL_SENDER = 'some_mail' # change to actual mail
    # for mail client
    MAIL_SERVER = 'some_smtp' # input smtp of your mail
    MAIL_PORT = 'some digits' # check on your smtp
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'some_mail' #input your mail
    MAIL_PASSWORD = 'some_password' # take from your mail configuration

class ProdConfig(BaseConfig):
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)
    SQLALCHEMY_DATABASE_URI = 'URI_from_heroku' # copy from heroku
    SECURITY_EMAIL_SENDER = 'some_mail' # change to actual mail
    # for mail client
    MAIL_SERVER = 'some_smtp' # input smtp of your mail
    MAIL_PORT = 'some digits' # check on your smtp
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'some_mail' #input your mail
    MAIL_PASSWORD = 'some_password' # take from your mail configuration



