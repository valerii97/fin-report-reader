import base64
import pandas as pd
import numpy as np
from flask_admin.contrib.sqla import ModelView
from flask_security import current_user

from app.plugins import db, admin
from app.auth_module.models import User
from app.dashapp.models import Reports



class Profiles(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    photo = db.Column(db.LargeBinary)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    user = db.relationship('User', backref='profiles', lazy='select')

    def __init__(self, name, photo, user_id):
        self.name = name
        self.photo = photo
        self.user_id = user_id

    def __repr__(self):
        return '<File %r>' % self.name


class Reports1(db.Model):
    __tablename__ = 'reports_by_clients'
    __table_args__ = (
        db.UniqueConstraint('filename', 'user_id', name='un_file_rep_cli'),
    )
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    data = db.Column(db.PickleType, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref='reports_by_client', lazy='select')

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

def change_view(view, context, model, name):
    #data = base64.decodestring(model.photo)
    return 'BLOB'

class ProfModelView(MyModelView):
    column_formatters = dict(photo = change_view)


admin.add_view(MyModelView(Reports1, db.session))
admin.add_view(ProfModelView(Profiles, db.session))


# adding data to database
def add_report_data1(filename, data, user_id):
    try:
        record = Reports1(filename, data, user_id)
        db.session.add(record)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        return 'Go fuck yourself, change filename!'
    return 'Succesfully loaded!'

def load_photo(name, photo, user_id):
    file = Profiles(name, photo, user_id)
    try:
        db.session.add(file)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print('cannot add file to DB: {}'.format(e))
        return False
    return True

def download_photo(user_id):
    try:
        file = Profiles.query.filter_by(user_id=user_id).first()
        if not file:
            print('Cannot find photo sqlalchemy')
            return False
        return file
    except:
        print('error to connect sqlalchmy')
    return False

def get_reports(table, user_id):
    try:
        list_reps = table.query.filter_by(user_id=user_id).all()
        if not list_reps:
            print('Cannot find reports in database!')
            return False
        return list_reps
    except Exception as e:
        print(e)
    return False

def delete_reports(table, report_id): 
    try:
        report = table.query.filter_by(id=report_id).first()
        db.session.delete(report)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print('cannot delete file from DB: {}'.format(e))
        return False
    return True


def preprocess_report(file, filename):
    try:
        if 'xlsx' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(file)
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(file)
    except Exception as e:
        print(e)
        return None

    if 'Manager' and 'Client' and 'Margin' in np.array(df):
        # creating list for columns
        new_df_cols = list(df.T[df.T.columns[0]])
        # deleting first row which will be columns of df
        df = df.drop([df.index[0]])
        # filling nan with 0
        df = df.fillna(0)
        # renaming columns
        df.columns = new_df_cols

        return df

    # Deleting nans
    df = df.dropna(axis=0, how='all')
    df = df.dropna(axis=1, how='all')
    # transposing
    df = df.T
    # deleting 1st row from df
    df = df.drop([df.index[0]])
    
    # transposing to create columns
    df = df.T
    # creating columns and deleting 1st nan item
    df_cols = list(df[df.columns[0]])
    df_cols.pop(0)
    df_cols = ['Months'] + df_cols

    # transposing to normal cond
    df = df.T
    # deleting 1st row and column with indexes and columns from df
    df = df.drop([df.index[0]])

    #df = df.drop([df.columns[0]], axis=1)
    #creating array with data from df
    data_arr = np.array(df)

    # creating correct df
    df_processed = pd.DataFrame(data_arr, columns=df_cols)
    # if 'GP %' in df_processed.columns:
    #     df_processed['GP %'] = 0
    # if 'NP %' in df_processed.columns:
    #     df_processed['NP %'] = 0
    df_processed = df_processed.fillna(0)
    # changing months
    month_arr = []
    for month in df_processed['Months']:
        month = month.replace('Current period\n', '')
        month = month.replace(',', '')
        month = ''.join([i for i in month if not i.isdigit()])
        month_arr.append(month)
    df_processed['Months'] = month_arr

    return df_processed

