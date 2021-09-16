from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_security import Security
from flask_mail import Mail


db = SQLAlchemy()
admin = Admin(name='Dashboard', template_mode='bootstrap4')
security = Security()
mail = Mail()
