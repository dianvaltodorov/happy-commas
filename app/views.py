import os
import csv
from app import app, db
from exceptions import InvalidUsage
from models import Entry
from flask import(
    render_template,
    request,
    send_from_directory,
    jsonify,
    after_this_request
)
from utils import(
    extract_user_id_attr_pairs,
    allowed_file,
    validate_params,
    create_entries_csv,
    get_entries_from_database,
    import_csv_data_in_db,
)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    """Process InvalidUsage exception and return a JSON response."""
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/export/', methods=['GET'])
def export():
    """
    Return a csv file with database entries.

    Combine query params in primary key pairs. Make db query.
    Return a populated csv file adn delete it afterwards
    """
    user_ids_param = request.args.get('user_ids', '')
    attrs_param = request.args.get('attributes', '')
    if not validate_params(user_ids_param, attrs_param):
        raise InvalidUsage('Get params are wrong', status_code=400)
    pk_pairs = extract_user_id_attr_pairs(user_ids_param, attrs_param)
    entries = get_entries_from_database(pk_pairs)
    csv_filename, csv_file_location = create_entries_csv(entries)
    response = send_from_directory(csv_file_location, csv_filename)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = \
        "attachment; filename=%s" % csv_filename

    @after_this_request
    def remove_file(response):
        """
        Delete the created file after the request is finish.
        """
        csv_path = os.path.join(csv_file_location, csv_filename)
        os.remove(csv_path)
        return response
    return response, 200


@app.route('/import', methods=['GET', 'POST'])
def import_csv():
    """
    Import data from csv file.
    Securely save csv file. Insert or update entries in database. Delete the
    uploaded file afterwards.
    """
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if not (uploaded_file and allowed_file(uploaded_file.filename)):
            raise InvalidUsage('No file uploaded', status_code=400)
        import_csv_data_in_db(uploaded_file)
        return ('', 200)
    return render_template('import.html')
