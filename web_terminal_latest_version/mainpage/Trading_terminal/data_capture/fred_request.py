#FRED REQUEST
import requests
import datetime
import pytz

# Your FRED API key
api_key = '03753ffca40483e479fc9a2b9793c510'

# Set up the endpoint and parameters
endpoint = 'https://api.stlouisfed.org/fred/series/observations'

def fred_data_request():
    end_date = datetime.datetime.now(pytz.timezone('US/Eastern'))
    start_date = end_date - datetime.timedelta(days=365)
    params = {
        'series_id': 'CPILFESL',  # Example series ID
        'api_key': api_key,
        'file_type': 'json',
        'start_date': start_date,
        'end_date' : end_date
    }

    # Make the HTTP request
    response = requests.get(endpoint, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        print(data)
    else:
        print("Failed to retrieve data:", response.status_code)
fred_data_request()