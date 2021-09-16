from flask_admin.contrib.sqla import ModelView
from flask_security import current_user

from app.plugins import db, admin
from app.auth_module.models import User


class Reports(db.Model):
    __table_args__ = (
        db.UniqueConstraint('filename', 'user_id', name='un_file_rep'),
    )
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    data = db.Column(db.PickleType, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref='reports', lazy='select')

    def __init__(self, filename, data, user_id):
        self.filename = filename
        self.data = data
        self.user_id = user_id

    def __repr__(self):
        return '<File %r>' % self.filename


class MyModelView(ModelView):
    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated and
                current_user.has_role('admin'))


admin.add_view(MyModelView(Reports, db.session))


# adding data to database
def add_report_data(filename, data, user_id):
    try:
        record = Reports(filename, data, user_id)
        db.session.add(record)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        return 'Go fuck yourself, change filename!'
    return 'Succesfully loaded!'

# exporting df


def export_report_data(filename, user_id):

    try:
        file = Reports.query.filter_by(filename=filename).all()
        if not file:
            print('Cannot find report in DB!')
            return False
        for f in file:
            if str(f.user_id) == user_id:
                return f
        else:
            print('You have no acsess to this data!')
    except:
        print('Error exporting file from DB!')
        return False

# exporting data for options in callback


def export_filenames(user_id):
    try:
        filenames = Reports.query.filter_by(user_id=user_id).all()
        if not filenames:
            print('Cannot find report in DB!')
            return False
        options = []
        for i in range(len(filenames)):
            options.append(filenames[i].filename)

        return options

    except:
        print('Error exporting filenames from DB!')
        return False
