from sqlalchemy import func, and_

from models.AQI import AQI
from models.County import County
from models.Elements import CO, NO2, Ozone, PM10, PM25, SO2
from models.State import State
from datetime import datetime


def get_table(element):
    return {
        'AQI': AQI,
        'CO': CO,
        'NO2': NO2,
        'Ozone': Ozone,
        'PM10': PM10,
        'PM25': PM25,
        'SO2': SO2
    }.get(element)


def get_column(pollutant_model, element):
    return getattr(pollutant_model, 'aqi' if element == 'AQI' else 'first_max_value')


def get_column_By_Attribute(pollutant_model, attribute):
    return getattr(pollutant_model, attribute)


def filter_by_date_state_county(query, pollutant_model, month, year, state=None, county=None):
    query = query.filter(
        func.extract('year', pollutant_model.date_local) == year,
    )

    if month:
        query = query.filter(
            func.extract('month', pollutant_model.date_local) == month
        )

    if state:
        query = query.join(State, State.state_code == pollutant_model.state_code) \
            .filter(State.state_name == state)

    if county:
        query = query.join(County, and_(
            pollutant_model.state_code == County.state_code,
            pollutant_model.county_code == County.county_code
        )).filter(County.county_name == county)
    return query


def get_average_value(element, year, month, state, county):
    pollutant_model = get_table(element)
    if not pollutant_model:
        return None

    column = get_column(pollutant_model, element)
    query = filter_by_date_state_county(pollutant_model.query, pollutant_model, month, year, state, county)
    query = query.with_entities(func.avg(column))

    average_value = query.scalar()
    return average_value


def get_row_count(element, year, month, state, county):
    pollutant_model = get_table(element)
    if not pollutant_model:
        return None

    query = filter_by_date_state_county(pollutant_model.query, pollutant_model, month, year, state, county)
    query = query.with_entities(func.count("date_local"))
    row_count = query.scalar()
    return row_count


def get_obs_count(element, year, month, state, county):
    pollutant_model = get_table(element)
    if not pollutant_model:
        return None

    query = filter_by_date_state_county(pollutant_model.query, pollutant_model, month, year, state, county)
    query = query.with_entities(func.sum(pollutant_model.observation_count))
    row_count = query.scalar()
    return row_count


def get_average_value_by_hour(element, year, month, state, county):
    pollutant_model = get_table(element)
    if not pollutant_model:
        return None

    column = get_column(pollutant_model, element)
    query = filter_by_date_state_county(pollutant_model.query, pollutant_model, month, year, state, county)

    query = query.with_entities(func.strftime('%H', pollutant_model.date_local).label('hour'),
                                func.avg(column).label('average_value')) \
        .group_by(func.strftime('%H', pollutant_model.date_local))

    results = query.all()

    average_values_by_hour = [{'name': result[0], 'average_value': result[1]} for result in results]

    return average_values_by_hour


def transform_to_day(dates):
    transformed_dates = []
    for date_entry in dates:
        date_obj = datetime.strptime(date_entry['time'], '%Y-%m-%d')

        day_of_week = date_obj.strftime('%A')

        transformed_dates.append({'name': day_of_week, 'value': date_entry['value']})

    return transformed_dates


def average_value_by_day(element, year, month, state, county):
    days = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday"
    }

    pollutant_model = get_table(element)
    if not pollutant_model:
        return None

    column = get_column(pollutant_model, element)
    query = filter_by_date_state_county(pollutant_model.query, pollutant_model, month, year, state, county)

    query = query.with_entities(pollutant_model.day_of_week, func.avg(column).label('value')).group_by(
        pollutant_model.day_of_week)
    result = query.all()
    result.sort(key=lambda x: x[0])
    # Convert the result to a dictionary for easier processing
    average_values = [{'name': days[row[0]], 'value': row[1]} for row in result]
    return average_values


def calculate_avg_value_by_season(element, year, state, county):
    pollutant_model = get_table(element)
    if not pollutant_model:
        return None

    column = get_column(pollutant_model, element)
    query = filter_by_date_state_county(pollutant_model.query, pollutant_model, None, year, state, county)

    query = query.with_entities(pollutant_model.season, func.avg(column).label('value')).group_by(
        pollutant_model.season)
    result = query.all()
    result.sort(key=lambda x: x[0])
    # Convert the result to a dictionary for easier processing
    average_values = [{'name': row[0], 'value': row[1]} for row in result]
    return average_values


def count_days_with_max_hour(element, year, month, state, county):
    pollutant_model = get_table(element)
    if not pollutant_model:
        return None

    query = filter_by_date_state_county(pollutant_model.query, pollutant_model, month, year, state, county)

    query = query.with_entities(pollutant_model.first_max_hour,
                                func.count(pollutant_model.first_max_hour).label('value')).group_by(
        pollutant_model.first_max_hour)
    result = query.all()
    result.sort(key=lambda x: x[0])

    # Convert the label values to 12-hour format with AM/PM
    def format_hour(hour):
        if hour == 0:
            return '12AM'
        elif hour < 12:
            return f'{hour}AM'
        elif hour == 12:
            return '12PM'
        else:
            return f'{hour - 12}PM'

    # Convert the result to a dictionary with formatted hour labels
    average_values = [{'name': format_hour(row[0]), 'value': row[1]} for row in result]
    return average_values


def avg_value_by_state(element, year, month):
    pollutant_model = get_table(element)
    if not pollutant_model:
        return None

    query = filter_by_date_state_county(pollutant_model.query, pollutant_model, month, year)
    column = get_column(pollutant_model, element)

    # Join with the states table to get the state name
    query = query.join(State, State.state_code == pollutant_model.state_code)

    # Assuming the pollutant_model has a 'value' column and the states_table has a 'state_name' column
    query = query.with_entities(State.state_name, func.avg(column).label('avg_value')).group_by(
        State.state_name)
    result = query.all()

    # Convert the result to a list of dictionaries
    average_values = [{'name': row[0], 'value': row[1]} for row in result]
    return average_values


def avg_value_by_county(element, year, month, state):
    pollutant_model = get_table(element)
    if not pollutant_model:
        return None

    query = filter_by_date_state_county(pollutant_model.query, pollutant_model, month, year, state)
    column = get_column(pollutant_model, element)

    # Join with the states table to get the state name
    query = query.join(County, and_(
        pollutant_model.state_code == County.state_code,
        pollutant_model.county_code == County.county_code
    ))

    # Assuming the pollutant_model has a 'value' column and the states_table has a 'state_name' column
    query = query.with_entities(County.county_name, func.avg(column).label('avg_value')).group_by(
        County.county_name)
    result = query.all()

    # Convert the result to a list of dictionaries
    average_values = [{'name': row[0], 'value': row[1]} for row in result]
    return average_values


def get_concern_levels_info(element, year, month, state, county):
    pollutant_model = get_table(element)
    if not pollutant_model:
        return None

    column = get_column(pollutant_model, element)
    query = filter_by_date_state_county(pollutant_model.query, pollutant_model, month, year, state, county)

    category_column = pollutant_model.category  # Assuming the column name is 'category'
    query = query.with_entities(column, category_column, pollutant_model)

    # Group by category and count occurrences
    query = query.group_by(category_column).with_entities(category_column, func.count().label('count'))

    results = query.all()

    table_format = [{'name': category, 'value': count} for category, count in results if count !=0]

    return table_format


def get_pollution_elements_info(year, month, state, county):
    elements = ['NO2', 'SO2', 'CO', 'PM10']
    pollution_info = []

    for element in elements:
        avg_value = get_average_value(element, year, month, state, county)
        pollution_info.append({'name': element, 'value': avg_value})

    return pollution_info
