import requests

class OpenMeteoAPI:
    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def get_latest_forecast(self):
        params = {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'current': 'temperature_2m,wind_speed_10m',
            'hourly': 'temperature_2m,relative_humidity_2m,wind_speed_10m'
        }
        response = requests.get(self.BASE_URL, params=params)
        response.raise_for_status()
        return response.json()