from app.profile_module.models import Reports1


# exporting df
def export_report_data(filename, user_id):
    try:
        file = Reports1.query.filter_by(filename=filename).all()
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
        filenames = Reports1.query.filter_by(user_id=user_id).all()
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