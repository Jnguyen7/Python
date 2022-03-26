from operator import mod
import requests
import datetime
import schedule
import time
import pandas as pd

api_key = '3492844594fa3402b5c5d03276ce4f55'

# List of All USA State Capitals including several famous cities
cities = ['Montgomery', 'Juneau', 'Phoenix', 'Little Rock', 'Sacramento', 'Denver', 'Hartford', 'Dover', 'Tallahassee', 'Atlanta', 'Honolulu', 'Boise', 'Springfield', 'Indianapolis', 'Des Moines', 'Topeka', 'Frankfort', 'Baton Rouge', 'Augusta', 'Annapolis', 'Boston', 'Lansing', 'Saint Paul', 'Jackson', 'Jefferson City', 'Helena', 'Lincoln', 'Carson City', 'Concord', 'Trenton', 'Santa Fe', 'Albany', 'Raleigh', 'Bismarck', 'Columbus', 'Oklahoma City', 'Salem', 'Harrisburg', 'Providence', 'Columbia', 'Pierre', 'Nashville', 'Austin', 'Houston', 'Salt Lake City', 'Montpelier', 'Richmond', 'Olympia', 'Charleston', 'Madison', 'Cheyenne', 'Los Angeles', 'New York City', 'Pittsburgh', 'Buffalo', 'Dallas', 'San Diego', 'Seattle']

# List of City data 
cities_weather = []

def get_response(city):
    response = requests.get(
        f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=imperial&APPID={api_key}"
    )
    return response

def get_data(newlist, cities):
    # Getting Today's date
    today = datetime.datetime.today()
    today_date = str(today).split()[0]
    today_time = str(today).split()[1]
    today_time = today_time.split('.')[0]

    for city in cities:
        # data
        city_data = get_response(city).json()

        weather_data = {
        'date' : today_date,
        'time' : today_time,
        'city' : city,
        'weather' : city_data['weather'][0]['main'],
        'temp' : city_data['main']['temp'],
        'temp_feels_like' : city_data['main']['feels_like'],
        'pressure' : city_data['main']['pressure'],
        'humidity' : city_data['main']['humidity'],
        'wind' : city_data['wind']['speed']
        }
        newlist.append(weather_data)
    
    return newlist

new_data = get_data(cities_weather, cities)

original_weather_data = pd.read_csv('weather_data.csv')

frames = [original_weather_data, new_data]
new_result = pd.concat(frames)

new_result.to_csv("weather_data.csv", mode = 'w+')