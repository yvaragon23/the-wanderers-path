import requests


class WeatherSim:
    """Fetches real-world weather data to put into the game"""
    def __init__(self, api_key, city):
        """Initializes the API with auth key, target city, and default weather"""
        self.api_key = api_key
        self.city = city
        self.condition = "Clear"
        self.temperature = 70.0

    def fetch(self):
        """Fetches weather data from OpenWeatherMap"""
        # URL from the API Docs (q=query, appid=password)
        url = f"https://api.openweathermap.org/data/2.5/weather?q={self.city}&appid={self.api_key}&units=imperial"
        try:
            # 5-second timeout so my game doesn't crash :)
            response = requests.get(url, timeout=5)
            # Raise an error if something went wrong
            response.raise_for_status()
            # We get something that python can't interpret, a JSON file which stands for
            # a JavaScript Object Notation so we use .json() to turn it into Python
            # dictionaries and lists
            data = response.json()
            # we grab our values for rain and temperature respectively
            self.condition = data["weather"][0]["main"]
            self.temperature = data["main"]["temp"]

        except Exception as e:
            print(f"Could not fetch weather. Using defaults."
                  f"Error: {e}")

"""
data["weather"][0]["main"] only returns "Clear","Clouds", "Rain", "Drizzle", "Thunderstorm"
"""