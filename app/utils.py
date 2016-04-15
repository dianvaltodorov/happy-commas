from app import db, app
import re
import os
import csv
from models import Entry
from sqlalchemy import or_, and_
from werkzeug import secure_filename
from exceptions import InvalidUsage


def fit_regex(s, regex):
    """Return if regular expression match s."""
    p = re.compile(regex)
    return p.match(s) is not None


def validate_params(user_ids_param, attrs_param):
    """Wrap the validation methods for the separate params."""
    return fit_regex(user_ids_param, app.config['USER_IDS_REGEX']) and \
        fit_regex(attrs_param, app.config['ATTRIBUTES_REGEX'])


def validate_csv_row(row):
    """Validate csv row contents"""
    return fit_regex(",".join(row), app.config['ALLOWED_CSV_ROW_FORMAT'])


def extract_user_id_attr_pairs(user_ids_param, attributes_param):
    """Extract user_id-attribute pairs from the passed query parameters.

    Example::

    user_ids_param = "1,2,3,4"
    attributes_param  = "name,age"
    return:[('1', 'names'), ('1', 'age'), ('2', 'names'), ('2', 'age'),
            ('3', 'names'), ('3', 'age'), ('4', 'names'), ('4', 'age')]
    """
    user_ids = user_ids_param.split(',')
    attributes = attributes_param.split(',')
    return [(ui, attr) for ui in user_ids for attr in attributes]


def get_entries_from_database(primary_key_pairs):
    """Return a list of entries for each pk pair."""
    entries = []
    for pair in primary_key_pairs:
        e = Entry.query.filter(Entry.user_id == pair[0],
                               Entry.key == pair[1]).first()
        if e is None:
            e = Entry(pair[0], pair[1], '')
        entries.append(e)
    return entries


def allowed_file(filename):
    """Filter wrong filenames."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


def delete_csv_file(dest):
    """Delete file"""
    os.remove(dest)


def create_entries_csv(entries):
    """Create csv file for export.Return a pair of filename and dest folder"""
    filename = 'data.csv'
    file_location = app.config['FILE_CREATION_FOLDER']
    path = os.path.join(file_location, filename)
    with open(path, 'wa') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for e in entries:
            writer.writerow(e.csv_repr())
    return filename, file_location


def import_csv_data_in_db(f):
    reader = csv.reader(f)
    for i, row in enumerate(reader):
        if validate_csv_row(row):
            e = Entry(row[0], row[1], row[2])
            db.session.merge(e)
        else:
            raise InvalidUsage('CSV file is broken on line %d' % i,
                               status_code=400)
    db.session.commit()
