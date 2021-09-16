from flask import url_for, render_template, redirect
from flask_security import current_user

def routes(main_app):
    @main_app.route('/')
    @main_app.route('/index')
    def index():
        if current_user.get_id():
            user_id = current_user.get_id()
            return redirect(url_for('profile.profile', user_id=user_id))
        return redirect(url_for('security.login'))


