from flask import Flask, abort, redirect, request, url_for
from flask_security import SQLAlchemyUserDatastore, current_user
from flask_security.forms import RegisterForm
from wtforms.fields import StringField
from wtforms.validators import DataRequired
from flask_admin import AdminIndexView

from app.dashapp.init_dash import register_dash
from app.dash2.init_dash2 import register_dash2
from app.dash_cli.init_dash_cli import register_dash_cli
from app.profile_module.controllers import profile_module
from app.plugins import db, security, admin
from app.auth_module.models import User, Role


def create_app(config_filename):

    app = Flask(__name__)

    app.config.from_object(config_filename)

    # init plugins
    db.init_app(app)
    # db.create_all(app=app)

    # initing flask-security
    # ========================================================================================
    class ExtendedRegisterForm(RegisterForm):
        name = StringField('Name', [DataRequired()])

    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, user_datastore, register_form=ExtendedRegisterForm)

    # initing admin
    # ========================================================================================
    class MyAdminIndexView(AdminIndexView):
        def is_accessible(self):
            return (current_user.is_active and
                    current_user.is_authenticated and
                    current_user.has_role('admin'))

        def _handle_view(self, name, **kwargs):
            """
            Override builtin _handle_view in order to redirect users when a view is not accessible.
            """
            if not self.is_accessible():
                if current_user.is_authenticated:
                    # permission denied
                    abort(403)
                else:
                    # login
                    return redirect(url_for('security.login', next=request.url))

    admin.init_app(app, index_view=MyAdminIndexView())

    # initing app context
    # ========================================================================================
    with app.app_context():

        # registering all except blueprints
        from .routes import routes
        routes(app)
        register_dash(app)
        register_dash2(app)
        register_dash_cli(app)

        # Register blueprint(s)
        app.register_blueprint(profile_module, url_prefix='/profile')

        return app
