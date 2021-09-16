import datetime

from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, current_user, logout_user
from flask_admin.contrib.sqla import ModelView
from flask_security import current_user

from app.plugins import db, admin

# Define models
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __init__(self, name, description):
        self.name = name
        self.description = description
    
    def __repr__(self):
        return '<{}>'.format(self.name)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean(), default=False)
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    
    def __init__(self, name, email, password, active, confirmed_at=None, roles=None):
        self.name = name
        self.email = email
        self.password = password
        self.active = active
        if not confirmed_at:
            self.confirmed_at = datetime.datetime.utcnow()
    
    def get_name(self):
        return str(self.name)

    def get_email(self):
        return str(self.email)
    
    def __repr__(self):
        return '<{}>'.format(self.name)


class MyModelView(ModelView):
    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated and
                current_user.has_role('admin'))


admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Role, db.session))