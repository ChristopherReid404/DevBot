#
# Weather Commands
#
import os
import requests
import shutil
from datetime import datetime

# Handles any commands that are prefixed with 'bot'
def handle_weather_command(command, user, channel, slack_client):
    commands = command.split()
    if len(commands) < 2:
        return 'missing'
    elif commands[1] == 'current':
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=fetch_current("Fredericton"),
            icon_emoji=':robot_face:'
        )
    elif commands[1] == 'daily':
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=fetch_daily("Fredericton"),
            icon_emoji=':robot_face:'
        )
    else:
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text="Current supported commands: current, daily",
            icon_emoji=':robot_face:'
        )
    return 'success'

WEATHER_API = 'http://api.openweathermap.org/data/2.5/weather?q='
API_KEY = '78b340763a57ca1e2c21f60f2c8eb5fc' # Not worried about this API Key being public

def fetch_daily(city):
    try:
        request = WEATHER_API + city + ",CA" + "&units=metric&APPID=" + API_KEY
        r = requests.get(request).json()

        temp_min = r["main"]["temp_min"]
        temp_max = r["main"]["temp_max"]
        sunset = r["sys"]["sunset"]
        sunrise = r["sys"]["sunrise"]

        forcast = "Sunrise: " + datetime.utcfromtimestamp(sunrise).strftime('%I:%M:%S %p') + ", Sunset: " + datetime.utcfromtimestamp(sunset).strftime('%I:%M:%S %p') + ", Max: " + str(temp_max) + "*c, Min: " + str(temp_min) + "*c."
        return True, forcast
    except:
        return False, "Unknown error"

def fetch_current(city):
    try:
        request = WEATHER_API + city + ",CA" + "&units=metric&APPID=" + API_KEY
        r = requests.get(request).json()
        
        weatherMain = r["weather"][0]["main"]
        weatherDesc = r["weather"][0]["description"]
        temp = r["main"]["temp"]

        forcast = "Fredericton's weather is " + str(weatherMain) + " (" + str(weatherDesc) + ") at " + str(temp) + "*c."
        return True, forcast
    except:
        return False, "Unknown error"

    # lat = r["coord"]["lat"]
    # lon = r["coord"]["lon"]
    # weatherMain = r["weather"][0]["main"]
    # weatherDesc = r["weather"][0]["description"]
    # weatherIcon = r["weather"][0]["icon"]
    # temp = r["main"]["temp"]
    # humidity = r["main"]["humidity"]
    # pressure = r["main"]["pressure"]
    # temp_min = r["main"]["temp_min"]
    # temp_max = r["main"]["temp_max"]
    # windSpeed = r["wind"]["speed"]
    # windDeg = r["wind"]["deg"]
    # clouds = r["clouds"]["all"]
    # sunset = r["sys"]["sunset"]
    # sunrise = r["sys"]["sunrise"]
    # cityId = r["id"]
