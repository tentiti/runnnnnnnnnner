@app.route('/nearest_courses', methods=['POST'])
def nearest_courses():
    latitude = float(request.form['latitude'])
    longitude = float(request.form['longitude'])
    print("Latitude: ", latitude, "Longitude: ", longitude)
    
    # Calculate distances
    distances = data.apply(lambda row: geodesic((latitude, longitude), (row['COURS_SPOT_LA'], row['COURS_SPOT_LO'])).km, axis=1)
    data['Distance'] = distances

    # Filter courses by distance
    under_5 = data[data['Distance'] <= 5].nsmallest(1, 'Distance')
    between_5_and_10 = data[(data['Distance'] > 5) & (data['Distance'] <= 10)].nsmallest(1, 'Distance')
    over_10 = data[data['Distance'] > 10].nsmallest(1, 'Distance')
    
    # Get weather data
    weather_info = requests.get(f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid=c7b88b5ac1aee004ce338ccee52a0265").json()
    print(weather_info)
    weather = weather_info['weather'][0]['description']
    
    return render_template('results.html', under_5=under_5, between_5_and_10=between_5_and_10, over_10=over_10, weather=weather)
