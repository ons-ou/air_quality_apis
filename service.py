from sqlalchemy import func

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


def filter_by_date_state_county(query, pollutant_model, month, year, state, county):
    query = query.filter(
        func.extract('year', pollutant_model.date_local) == year,
        func.extract('month', pollutant_model.date_local) == month
    )

    if state:
        query = query.join(State, State.state_code == pollutant_model.state_code) \
            .filter(State.state_name == state)

    if county:
        query = query.join(County) \
            .filter(County.county_name == county)
    return query


def get_average_value(element, year, month, state, county, attribute='aqi'):
    pollutant_model = get_table(element)
    if not pollutant_model:
        return None

    column = get_column(pollutant_model, element)
    query = filter_by_date_state_county(pollutant_model.query, pollutant_model, month, year, state, county)
    query = query.with_entities(func.avg(column))

    average_value = query.scalar()
    return average_value


def get_row_count(element, year, month, state, county, attribute):
    pollutant_model = get_table(element)
    if not pollutant_model:
        return None

    column = get_column_By_Attribute(pollutant_model, attribute)
    query = filter_by_date_state_county(pollutant_model.query, pollutant_model, month, year, state, county)
    query = query.with_entities(func.count(column))
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

    average_values_by_hour = [{'hour': result[0], 'average_value': result[1]} for result in results]

    return average_values_by_hour


def transform_to_day(dates):
    transformed_dates = []
    for date_entry in dates:
        date_obj = datetime.strptime(date_entry['time'], '%Y-%m-%d')

        day_of_week = date_obj.strftime('%A')

        transformed_dates.append({'day': day_of_week, 'value': date_entry['value']})

    return transformed_dates


def average_value_by_day(element, year, month, state, county, attribute='aqi'):
    pollutant_model = get_table(element)
    if not pollutant_model:
        return None

    column = get_column(pollutant_model, element)
    query = filter_by_date_state_county(pollutant_model.query, pollutant_model, month, year, state, county)

    # Group data by day and calculate the average value for each day
    query = query.with_entities(func.TO_CHAR(pollutant_model.date_local, 'YYYY-MM-DD').label('day'),
                                func.avg(column).label('average_value')) \
        .group_by(func.TO_CHAR(pollutant_model.date_local, 'YYYY-MM-DD'))

    # Execute the query
    results = query.all()

    # Convert the query results to a list of dictionaries
    average_values_by_day = [{'time': result[0], 'value': result[1]} for result in results]

    # Transform the dates to days of the week
    transformed_dates = transform_to_day(average_values_by_day)

    return transformed_dates


def calculate_season_from_date(month):
    seasons = {
        1: 'Winter',
        2: 'Winter',
        3: 'Spring',
        4: 'Spring',
        5: 'Spring',
        6: 'Summer',
        7: 'Summer',
        8: 'Summer',
        9: 'Fall',
        10: 'Fall',
        11: 'Fall',
        12: 'Winter'
    }
    return seasons.get(int(month))


def calculate_avg_value_by_season(element, year, month, state, county, attribute='aqi'):
    pollutant_model = get_table(element)
    if not pollutant_model:
        return None

    column = get_column(pollutant_model, element)
    query = pollutant_model.query.filter(
        func.extract('year', pollutant_model.date_local) == year
    )

    if state:
        query = query.join(State, State.state_code == pollutant_model.state_code) \
            .filter(State.state_name == state)

    if county:
        query = query.join(County) \
            .filter(County.county_name == county)

    query = query.with_entities(
        func.TO_CHAR(pollutant_model.date_local, 'MM').label('month'),
        func.avg(column).label('average_value')
    ).group_by(func.TO_CHAR(pollutant_model.date_local, 'MM'))

    results = query.all()
    print(results)
    average_values = [{'season': calculate_season_from_date(result.month), 'average_value': float(result.average_value)}
                      for result in results]
    print(average_values)
    return average_values


def count_days_with_max_hour(element, year, month, state, county, first_max_hour, attribute='aqi'):
    pollutant_model = get_table(element)
    if not pollutant_model:
        return None
    query = filter_by_date_state_county(pollutant_model.query, pollutant_model, month, year, state, county)
    query = query.filter(pollutant_model.first_max_hour == first_max_hour)
    distinct_dates_count = query.with_entities(func.count(func.distinct(pollutant_model.date_local))).scalar()

    return distinct_dates_count
