from flask import request, jsonify

from config import app
from service import get_average_value, get_row_count


def get_request_parameters():
    element = request.args.get('element')
    year = request.args.get('year')
    month = request.args.get('month')
    state = request.args.get('state')
    county = request.args.get('county')
    return element, year, month, state, county


@app.route("/")
def heartbeat():
    return 'Server is running'


@app.route("/average_value", methods=['GET'])
def average_value():
    element, year, month, state, county = get_request_parameters()

    average = get_average_value(element, year, month, state, county)
    if average is None:
        return jsonify({'error': 'Invalid parameters or data not found'}), 400

    return jsonify({'average_value': average}), 200


@app.route('/count', methods=['GET'])
def get_row_count_api():
    element, year, month, state, county = get_request_parameters()

    row_count = get_row_count(element, year, month, state, county)

    if row_count is None:
        return jsonify({'error': 'Invalid element'}), 400

    return jsonify({'count': row_count})


# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
from config import app

if __name__ == '__main__':
    app.run()
