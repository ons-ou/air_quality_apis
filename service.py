from sqlalchemy import func

from models.AQI import AQI
from models.County import County
from models.Elements import CO, NO2, Ozone, PM10, PM25, SO2
from models.State import State


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

