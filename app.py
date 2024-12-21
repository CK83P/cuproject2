from flask import Flask, request, render_template, jsonify
import requests
import json

app = Flask(__name__)

#  API-клюс и сайт для запросов
API_KEY = 'VWsAfpp1cR94r215t2Q5ehq6eGqSpMgp'
BASE_URL = 'http://dataservice.accuweather.com'


# Функция для ключа города
def get_key_city(city_name):
    location_url = f"{BASE_URL}/locations/v1/cities/search"
    params = {
        'q': city_name,
        'apikey': API_KEY,
        'language': 'ru-ru'
    }
    response = requests.get(location_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data:  # Если данные не пустые
            city_key = data[0]["Key"]
            return city_key
        else:
            return None  # Город не найден
    else:
        print(f"Ошибка запроса: {response.status_code}")
        return None


# Функция для получения погодных данных
def get_data_weather(city):
    city_key = get_key_city(city)
    url = f'{BASE_URL}/currentconditions/v1/{city_key}'
    params = {'apikey': API_KEY, 'details': 'true'}

    response = requests.get(url, params=params)
    print(response.json())
    if response.status_code == 200:
        return response.json()[0]
    else:
        return None


# Функция для оценки неблагоприятных погодных условий
def check_bad_weather(temperature, wind_speed, precipitation_value):
    if temperature < 0 or temperature > 35:
        return "неблагоприятные"
    if wind_speed > 50:
        return "неблагоприятные"
    if precipitation_value > 70:
        return "неблагоприятные"
    return "благоприятные"


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        start_city = request.form['start_city']
        end_city = request.form['end_city']

        # Получение погодных данных для начального города
        start_weather_data = get_data_weather(start_city)
        # Получение погодных данных для конечного города
        end_weather_data = get_data_weather(end_city)

        if start_weather_data and end_weather_data:
            # Данные для начального города
            start_temperature = start_weather_data['Temperature']['Metric']['Value']
            start_wind_speed = start_weather_data['Wind']['Speed']['Metric']['Value']
            start_precipitation_value = (start_weather_data['PrecipitationSummary']['Precipitation']['Metric']['Value'] * 100)
            start_weather_condition = check_bad_weather(start_temperature, start_wind_speed, start_precipitation_value)

            # Данные для конечного города
            end_temperature = end_weather_data['Temperature']['Metric']['Value']
            end_wind_speed = end_weather_data['Wind']['Speed']['Metric']['Value']
            end_precipitation_value = (end_weather_data['PrecipitationSummary']['Precipitation']['Metric']['Value'] * 100)
            end_weather_condition = check_bad_weather(end_temperature, end_wind_speed, end_precipitation_value)

            return render_template('result.html',
                                   start_temperature=start_temperature,
                                   start_wind_speed=start_wind_speed,
                                   start_precipitation_probability=start_precipitation_value,
                                   start_weather_condition=start_weather_condition,
                                   end_temperature=end_temperature,
                                   end_wind_speed=end_wind_speed,
                                   end_precipitation_probability=end_precipitation_value,
                                   end_weather_condition=end_weather_condition)
        else:
            return render_template('error.html', message="Ошибка получения данных о погоде.")

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
