from flask import Flask, request, render_template
import pandas as pd
from geopy.distance import geodesic
import requests
import os

app = Flask(__name__)
weather_api_key = os.getenv('OPENWEATHERMAP_API_KEY')

# Load the data
data = pd.read_csv('KC_CFR_WLK_STRET_INFO_2021.csv', na_values='-')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/nearest_courses', methods=['POST'])
def nearest_courses():
    latitude = float(request.form['latitude'])
    longitude = float(request.form['longitude'])
    
    # Calculate distances
    distances = data.apply(lambda row: geodesic((latitude, longitude), (row['COURS_SPOT_LA'], row['COURS_SPOT_LO'])).km, axis=1)
    data['Distance'] = distances

    # Filter courses by distance
    under_5 = data[data['COURS_LT_CN'] =='1~5Km미만'].nsmallest(1, 'Distance')
    between_5_and_10 = data[(data['COURS_LT_CN'] =='5~10Km미만')].nsmallest(1, 'Distance')
    over_10 = data[data['COURS_LT_CN'].isin(['10~15Km미만', '15~20Km미만', '20~100Km미만'])].nsmallest(1, 'Distance')

    # Get weather data
    weather_info = requests.get(f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={weather_api_key}&lang=kr&units=metric").json()
    weather = str(weather_info['main']['feels_like'])+'°C의 체감 온도로 '+weather_info['weather'][0]['description']
    
    return render_template('results.html', under_5=under_5, between_5_and_10=between_5_and_10, over_10=over_10, weather=weather)

@app.route('/search', methods=['POST'])
def search():
    region_name = request.form['region']
    filtered_courses = data[data['SIGNGU_NM'].str.contains(region_name)]
    distances = filtered_courses['Distance'].sort_values()
    return render_template('search_results.html', courses=filtered_courses, distances=distances)

if __name__ == '__main__':
    app.run(debug=True)
