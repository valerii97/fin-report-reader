import dash
from .layout import layout
from .callbacks import register_callbacks
from flask_security import login_required, roles_required


def register_dash_cli(server):

    app = dash.Dash(__name__,
                    server=server,
                    routes_pathname_prefix='/dash-cli/')

    with server.app_context():
        app.title = 'Client reports'
        app.layout = layout

        register_callbacks(app)
    # app.css.append_css({'external_url':'/assets/style.css'})
    protect_dashviews(app)


def protect_dashviews(dashapp):
    for view_func in dashapp.server.view_functions:
        if view_func.startswith(dashapp.config.routes_pathname_prefix):
            dashapp.server.view_functions[view_func] = \
                login_required(dashapp.server.view_functions[view_func])

    for view_func in dashapp.server.view_functions:
        if view_func.startswith(dashapp.config.routes_pathname_prefix):
            dashapp.server.view_functions[view_func] = \
                roles_required('user')(
                    dashapp.server.view_functions[view_func])
