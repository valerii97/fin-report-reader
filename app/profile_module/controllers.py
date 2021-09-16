import base64
import io

from flask import url_for, render_template, redirect, Blueprint, request, Response, flash
from flask_security import current_user, login_required
import pandas as pd
from werkzeug.exceptions import RequestEntityTooLarge

from app.dashapp.models import export_filenames, add_report_data, Reports
from .models import load_photo, download_photo, get_reports, preprocess_report, \
    delete_reports, add_report_data1, Reports1
from app.plugins import db


profile_module = Blueprint('profile', __name__)


# for loading photo
@profile_module.route('/upload', methods=['post'])
@login_required
def upload():
    user_id = current_user.get_id()
    file = request.files['upload_file']
    filename = file.filename
    data = file.read()
    photograph = download_photo(user_id)
    if photograph:
        photograph.name = filename
        photograph.photo = data
        db.session.commit()
        flash('Photo changed succesfully!', category='succes')
        return redirect(url_for('.profile', user_id=user_id))  # photo changed
    res = load_photo(filename, data, user_id)
    if res:
        flash('Photo loaded succesfully!', category='succes')
        return redirect(url_for('.profile', user_id=user_id))  # photo loaded first time
    flash("Photo hasn't been updated!", category='error')
    return redirect(url_for('.profile', user_id=user_id))  # photo hasnt been added/updated


# for rendering profile page
@profile_module.route('/<int:user_id>', methods=['post', 'get'])
@login_required
def profile(user_id=None):
    user_id = current_user.get_id()
    reports_by_clients = get_reports(Reports1, user_id)
    file = download_photo(user_id)
    reports = get_reports(Reports, user_id)
    reps = []
    reps_by_cli = []
    if reports:
        for r in reports:
            dictionary = {'url':'/dash/', 'filename':r.filename, 'value':r.id}
            reps.append(dictionary)
    if reports_by_clients:
        for r in reports_by_clients:
            dictionary = {'url':'/dash2/', 'filename':r.filename, 'value':r.id}
            reps_by_cli.append(dictionary)
    if file:
        image = base64.b64encode(file.photo).decode('ascii')
    else:
        image = False
    return render_template('profile/profile.html', 
    title='Profile', 
    username=current_user.get_name(),
    email=current_user.get_email(),
    image=image,
    user_id=user_id,
    reps=reps,
    reps_by_cli=reps_by_cli)

# for loading reports
@profile_module.route('/load-report', methods=['post'])
@login_required
def load_report():
    user_id = current_user.get_id()
    file = request.files['upload_report']
    filename = file.filename
    # checking gen reps if downloaded with same filename
    reports = get_reports(Reports, user_id)
    if reports:
        for r in reports:
            if r.filename == filename:
                flash('Report with this name has been already loaded.', category='alert_gen')
                return redirect(url_for('.profile', user_id=user_id))
    # cheking client reps if downloaded with same filename
    reps_by_clients = get_reports(Reports1, user_id)
    if reps_by_clients:
        for r in reps_by_clients:
            if r.filename == filename:
                flash('Report with this name has been already loaded.', category='alert_cli')
                return redirect(url_for('.profile', user_id=user_id))
    df = preprocess_report(file, filename)
    # checking if client report was downloaded
    if 'Client' and 'Manager' and 'Margin' in list(df.columns):
        try:
            res = add_report_data1(filename, df, user_id)
            flash('Report downloaded succesfully!', category='succes-load-cli-rep')
            return redirect(url_for('.profile', user_id=user_id)) # client report downloaded
        except Exception as e:
            print(e)
    try:
        res = add_report_data(filename, df, user_id)
        flash('Report downloaded succesfully!', category='succes-load-gen-rep')
        return redirect(url_for('.profile', user_id=user_id)) # gen report downloaded
    except Exception as e:
        print(e)
    flash('Error during report loading!', category='error-rep-load')
    return redirect(url_for('.profile', user_id=user_id)) # no report was downloaded due to some errors


# deleting report general
@profile_module.route('/delete-report', methods=['post'])
@login_required
def delete_report():
    report_id = request.form['id']
    user_id = current_user.get_id()
    try:
        res = delete_reports(Reports, report_id)
        flash('Report succesfully deleted!', category='deleted_gen')
        return redirect(url_for('.profile', user_id=user_id))
    except Exception as e:
        print(e)
    flash('Cannont delete report!', category='del_rep_error_gen')
    return redirect(url_for('.profile', user_id=user_id))


# deleting report by clients
@profile_module.route('/delete-report-by-client', methods=['post'])
@login_required
def delete_report_by_client():
    report_id = request.form['id']
    user_id = current_user.get_id()
    try:
        res = delete_reports(Reports1, report_id)
        flash('Report succesfully deleted!', category='deleted_cli')
        return redirect(url_for('.profile', user_id=user_id))
    except Exception as e:
        print(e)
    flash('Cannont delete report!', category='del_rep_error_gen_cli')
    return redirect(url_for('.profile', user_id=user_id))