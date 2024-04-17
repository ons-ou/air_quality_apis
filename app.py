from flask import request, jsonify

from config import app
from service import get_average_value, get_row_count, average_value_by_day, calculate_avg_value_by_season, \
    count_days_with_max_hour, get_obs_count, avg_value_by_state, avg_value_by_county


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


@app.route('/observation_count', methods=['GET'])
def get_obs_count_api():
    element, year, month, state, county = get_request_parameters()

    row_count = get_obs_count(element, year, month, state, county)

    if row_count is None:
        return jsonify({'error': 'Invalid element'}), 400

    return jsonify({'count': row_count})


@app.route('/avg_by_day', methods=['GET'])
def get_average_value_by_day():
    element, year, month, state, county = get_request_parameters()
    average_values = average_value_by_day(element, year, month, state, county)

    if average_values is None:
        return jsonify({'error': 'Invalid element or no data found'}), 400

    return jsonify(average_values)


@app.route('/avg_by_season', methods=['GET'])
def avg_value_by_season():
    element, year, month, state, county = get_request_parameters()

    # Call the function to retrieve average values by season
    average_values = calculate_avg_value_by_season(element, year, state, county)

    if average_values is None:
        return jsonify({'error': 'Invalid element or no data found'}), 400

    return jsonify(average_values)


@app.route('/max_hours', methods=['GET'])
def nb_day_by_hour():
    element, year, month, state, county = get_request_parameters()
    average_values = count_days_with_max_hour(element, year, month, state, county)

    if average_values is None:
        return jsonify({'error': 'Invalid element or no data found'}), 400

    return jsonify(average_values)


@app.route('/avg_by_state', methods=['GET'])
def avg_by_state():
    element, year, month, _, _ = get_request_parameters()
    average_values = avg_value_by_state(element, year, month)

    if average_values is None:
        return jsonify({'error': 'Invalid element or no data found'}), 400

    return jsonify(average_values)


@app.route('/avg_by_county', methods=['GET'])
def avg_by_county():
    element, year, month, state, _ = get_request_parameters()
    average_values = avg_value_by_county(element, year, month, state)

    if average_values is None:
        return jsonify({'error': 'Invalid element or no data found'}), 400

    return jsonify(average_values)


# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
from config import app

if __name__ == '__main__':
    app.run()
