#!/bin/python3

# What this program does

from zoneinfo import ZoneInfo
from datetime import datetime
import pytz
import yagmail
import openmeteo_requests
import pandas as pd
from retry_requests import retry
from pretty_html_table import build_table

import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry
import requests

## Weather API - OpenMateo
# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": -00.0000,
	"longitude": 000.0000,
	"daily": ["temperature_2m_max", "temperature_2m_min", "sunrise", "sunset", "uv_index_max", "precipitation_sum", "rain_sum", "showers_sum", "snowfall_sum", "precipitation_probability_max", "wind_speed_10m_max"],
	"timezone": "Australia/Sydney",
	"forecast_days": 1
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates {response.Latitude()}°E {response.Longitude()}°N")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

# Process daily data. The order of variables needs to be the same as requested.
daily = response.Daily()
daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
daily_sunrise = daily.Variables(2).ValuesAsNumpy()
daily_sunset = daily.Variables(3).ValuesAsNumpy()
daily_uv_index_max = daily.Variables(4).ValuesAsNumpy()
daily_precipitation_sum = daily.Variables(5).ValuesAsNumpy()
daily_rain_sum = daily.Variables(6).ValuesAsNumpy()
daily_showers_sum = daily.Variables(7).ValuesAsNumpy()
daily_snowfall_sum = daily.Variables(8).ValuesAsNumpy()
daily_precipitation_probability_max = daily.Variables(9).ValuesAsNumpy()
daily_wind_speed_10m_max = daily.Variables(10).ValuesAsNumpy()

daily_data = {"date": pd.date_range(
	start = pd.to_datetime(daily.Time(), unit = "s"),
	end = pd.to_datetime(daily.TimeEnd(), unit = "s"),
	freq = pd.Timedelta(seconds = daily.Interval()),
	inclusive = "left"
)}
daily_data["Max Temp"] = daily_temperature_2m_max
daily_data["Min Temp"] = daily_temperature_2m_min
daily_data["Sunrise"] = daily_sunrise
daily_data["Sunset"] = daily_sunset
daily_data["Max UV Index"] = daily_uv_index_max
daily_data["Precip Sum"] = daily_precipitation_sum
daily_data["Rain"] = daily_rain_sum
daily_data["Showers"] = daily_showers_sum
daily_data["Snowfall"] = daily_snowfall_sum
daily_data["Precip Chance"] = daily_precipitation_probability_max
daily_data["Max Wind"] = daily_wind_speed_10m_max

daily_dataframe = pd.DataFrame(data = daily_data)
print(daily_dataframe)

weather = build_table(daily_dataframe, 'blue_dark')
# save to html file
with open('pretty_table.html','w') as f:
    f.write(weather)

## Quote API
# Quote API Request Details
url = "https://zenquotes.io/api/today"

# Making http request
response = requests.post(url)
print(response.json())

# Get JSON response
data = response.json()

# Get the value of "h" key (html) and convert it to a string
quote_list = []

# iterate over the list of dictionaries
for item in data:
    # check if any 'h' key existing in dict
    if 'h' in item:
        # Get the value of the 'h' key, convert it to string and append
        quote_list.append(str(item['h']))

# Convert the list into a string
quote = ' '.join(quote_list)
print(quote)

## Open email template
standard = open("standard.html")
# Creates a new email html doc.
#email_to_send = open("email_to_send.html", "w")
email_body = ''
app_pwd = 'INSERT_APP_PWD_HERE'
email = 'YOUREMAIL@HOST.com'
send_to = 'RECIPIENT@HOST.com'
subject = 'YOUR DAILY FORECAST & QUOTE!!!'

receiver = 'INSERT_NAME'
location = 'Country/City'
datetime = datetime.now(pytz.timezone(location)).strftime("%Y-%m-%d %H:%M:%S")

print(datetime)

for line in standard:
    if "RECEIVER" in line:
        line = line.replace("RECEIVER",receiver)
    if "LOCATION" in line:
        line = line.replace("LOCATION",location)
    if "DATETIME" in line:
        line = line.replace("DATETIME",datetime)
    if "WEATHER" in line:
        line = line.replace("WEATHER",weather)
    if "QUOTE" in line:
        line = line.replace("QUOTE_TODAY",quote)

    #email_to_send.write(line)
    email_body += line

with yagmail.SMTP(email,app_pwd) as yag:
    yag.send(send_to,subject,email_body)
    print('sent')