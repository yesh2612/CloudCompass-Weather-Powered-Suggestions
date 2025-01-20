from google.cloud import datastore
from .model import Model

class DatastoreModel(Model):
    def __init__(self):
        self.client = datastore.Client()

    def _get_city_key(self, city):
        """Generate a unique key for a city."""
        return self.client.key("CityInfo", city)

    def add_city_info(self, data):
        """
        Add or update city information in the datastore.
        Ensure only one entry exists per city.
        """
        city_key = self._get_city_key(data["city"])
        city_entity = self.client.get(city_key)

        if city_entity:
            city_entity["weather"] = data["weather"]
            city_entity["recommendations"] = data["recommendations"]
            print(f"City {data['city']} updated with the latest information.")
        else:
            city_entity = datastore.Entity(key=city_key)
            city_entity["city"] = data["city"]
            city_entity["weather"] = data["weather"]
            city_entity["recommendations"] = data["recommendations"]
            print(f"City {data['city']} added to the datastore.")

        self.client.put(city_entity)

    def get_city_info(self, city):
        """
        Retrieve city information from the datastore.
        """
        city_key = self._get_city_key(city)
        city_entity = self.client.get(city_key)
        if city_entity:
            return {
                "city": city_entity["city"],
                "weather": city_entity["weather"],
                "recommendations": city_entity["recommendations"],
            }
        return None

    # Implementation of abstract methods
    def get_recommendations(self, weather_condition):
        """Retrieve recommendations based on weather (not used here)."""
        return "Not implemented in DatastoreModel."

    def get_weather_info(self, city):
        """Retrieve weather information for a city (not used here)."""
        return "Not implemented in DatastoreModel."

