from abc import ABC, abstractmethod

class Model(ABC):
    @abstractmethod
    def get_weather_info(self, city):
        pass

    @abstractmethod
    def get_recommendations(self, weather_condition):
        pass

    @abstractmethod
    def add_city_info(self, data):
        pass

