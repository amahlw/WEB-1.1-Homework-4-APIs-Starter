
# DON'T FORGET TO RUN (python3 app.py) IN TERMINAL
# -----------------------------------------------------------------


import os
import requests

from pprint import PrettyPrinter
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, render_template, request, send_file
from geopy.geocoders import Nominatim


################################################################################
# SETUP
################################################################################

app = Flask(__name__)

# Get the API key from the '.env' file
load_dotenv()
API_KEY = os.getenv('API_KEY')

pp = PrettyPrinter(indent=4)


################################################################################
# ROUTES
################################################################################

@app.route('/')
def home():
    """Displays the homepage with forms for current or historical data."""
    context = {
        'min_date': (datetime.now() - timedelta(days=5)),
        'max_date': datetime.now()
    }
    return render_template('home.html', **context)


def get_letter_for_units(units):
    """Returns a shorthand letter for the given units."""
    return 'F' if units == 'imperial' else 'C' if units == 'metric' else 'K'


@app.route('/results')
def results():
    """Displays results for current weather conditions."""
    # TODO: Use 'request.args' to retrieve the city & units from the query
    # parameters.
    city = request.args.get('city')
    units = request.args.get('units')

    url = 'http://api.openweathermap.org/data/2.5/weather'
    params = {
        # TODO: Enter query parameters here for the 'appid' (your api key),
        # the city, and the units (metric or imperial).
        # See the documentation here: https://openweathermap.org/current

        'appid': API_KEY,

        'q': city,
        'units': units


    }

    results = requests.get(url, params=params).json

    # Uncomment the line below to see the results of the API call!
    pp.pprint(results)

    # TODO: Replace the empty variables below with their appropriate values.
    # You'll need to retrieve these from the result_json object above.

    # For the sunrise & sunset variables, I would recommend to turn them into
    # datetime objects. You can do so using the `datetime.fromtimestamp()`
    # function.

    sunrise = datetime.fromtimestamp(results['sys']['sunrise'])
    sunset = datetime.fromtimestamp(results['sys']['sunset'])

    context = {
        'date': datetime.now(),
        'city': city,
        'description': results['weather'][0]['description'],
        'temp': results['main']['temp'],
        'humidity': results['main']['humidity'],
        'wind_speed': results['wind']['speed'],
        'sunrise': sunrise,
        'sunset': sunset,
        'units_letter': get_letter_for_units(units)
    }

    return render_template('results.html', **context)


def get_min_temp(results):
    """Returns the minimum temp for the given hourly weather objects."""
    # TODO: Fill in this function to return the minimum temperature from the
    # hourly weather data.
    bottom_temp = results[0]['temp']

    for temp in results:
        if bottom_temp > temp['temp']:
            bottom_temp = temp['temp']

    return bottom_temp


def get_max_temp(results):
    """Returns the maximum temp for the given hourly weather objects."""
    # TODO: Fill in this function to return the maximum temperature from the
    # hourly weather data.

    high_temp = results[0]['temp']

    for obj in results:
        if high_temp < obj['temp']:
            high_temp = obj['temp']

    return high_temp


def get_lat_lon(city_name):
    geolocator = Nominatim(user_agent='Weather Application')
    location = geolocator.geocode(city_name)
    if location is not None:
        return location.latitude, location.longitude
    return 0, 0


@app.route('/historical_results')
def historical_results():
    """Displays historical weather forecast for a given day."""
    # TODO: Use 'request.args' to retrieve the city & units from the query
    # parameters.
    city = request.args.get('city')
    date = request.args.get('date')
    units = request.args.get('units')
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    date_in_seconds = date_obj.strftime('%s')

    latitude, longitude = get_lat_lon(city)

    url = 'http://api.openweathermap.org/data/2.5/onecall/timemachine'
    params = {
        # TODO: Enter query parameters here for the 'appid' (your api key),
        # latitude, longitude, units, & date (in seconds).
        # See the documentation here (scroll down to "Historical weather data"):
        # https://openweathermap.org/api/one-call-api
        'appid': API_KEY,

        'lat': latitude,
        'lon': longitude,
        'units': units,
        'ds': date_in_seconds

    }

    result_json = requests.get(url, params=params).json()

    # Uncomment the line below to see the results of the API call!
    pp.pprint(result_json)

    result_current = result_json['current']
    result_hourly = result_json['hourly']

    # TODO: Replace the empty variables below with their appropriate values.
    # You'll need to retrieve these from the 'result_current' object above.

    city = result_current["name"]
    description = result_current['weather'][0]['description']
    temp = result_current['main']['temp']

    context = {
        'city': city,
        'date': date_obj,
        'lat': latitude,
        'lon': longitude,
        'units': units,
        # should be 'C', 'F', or 'K'
        'units_letter': get_letter_for_units(units),
        'description': description,
        'temp': temp,
        'min_temp': get_min_temp(result_hourly),
        'max_temp': get_max_temp(result_hourly)
    }

    return render_template('historical_results.html', **context)


if __name__ == '__main__':
    app.run(debug=True)
