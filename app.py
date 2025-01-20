from flask import Flask, request, jsonify, render_template
from gbmodel.model_datastore import DatastoreModel
import requests
import os

model = DatastoreModel()

app = Flask(__name__)

# API keys
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
KG_API_KEY = os.getenv("KG_API_KEY")
PLACES_API_KEY = os.getenv("PLACES_API_KEY")

# Home route
@app.route("/")
def index():
    """Render the homepage."""
    return render_template("index.html")

# Function to recommend places based on weather
def recommend_places(places, weather_condition):
    """
    Recommend places to visit based on specific weather conditions.
    """
    if weather_condition in ["thunderstorm", "storm", "haze"]:
        return [], "It's not a good time to visit due to uncertain weather conditions."

    recommendations = []
    for place in places:
        place_types = place.get("types", [])
        if weather_condition in ["clear", "sunny"]:
            if any(pt in place_types for pt in ["park", "tourist_attraction", "landmark", "garden"]):
                recommendations.append(place)
        elif weather_condition in ["rain", "drizzle"]:
            if any(pt in place_types for pt in ["museum", "temple", "shopping_mall", "art_gallery", "aquarium"]):
                recommendations.append(place)
        elif weather_condition in ["mist", "clouds"]:
            if any(pt in place_types for pt in ["viewpoint", "park", "museum", "landmark"]):
                recommendations.append(place)
        elif weather_condition in ["snow"]:
            if any(pt in place_types for pt in ["museum", "ski_resort", "indoor_arena", "art_gallery"]):
                recommendations.append(place)
        elif weather_condition in ["wind"]:
            if any(pt in place_types for pt in ["library", "cafe", "cultural_center", "shopping_mall"]):
                recommendations.append(place)
        if len(recommendations) >= 5:
            break
    if not recommendations:
        return [], "There are no tourist places to recommend."

    return recommendations, None

# API route to fetch information
@app.route("/get_city_info", methods=["POST"])
def get_city_info():
    """Fetch city information including weather, knowledge graph, and places."""
    city = request.form.get("city")
    if not city:
        return jsonify({"error": "City name is required"}), 400

    weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    weather_response = requests.get(weather_url)

    if weather_response.status_code != 200:
        return jsonify({"error": "City not found or weather API error"}), weather_response.status_code

    weather_data = weather_response.json()
    weather_condition = weather_data["weather"][0]["main"].lower()

    kg_url = "https://kgsearch.googleapis.com/v1/entities:search"
    kg_params = {"query": city, "key": KG_API_KEY, "limit": 1, "indent": True}
    kg_response = requests.get(kg_url, params=kg_params)

    if kg_response.status_code != 200:
        return jsonify({"error": "Knowledge Graph API error"}), kg_response.status_code

    kg_data = kg_response.json()
    city_info = kg_data.get("itemListElement", [{}])[0].get("result", {}).get("detailedDescription", {}).get("articleBody", "No details available.")

    places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    lat, lon = weather_data["coord"]["lat"], weather_data["coord"]["lon"]
    places_params = {
        "location": f"{lat},{lon}",
        "radius": 5000,
        "type": "tourist_attraction",
        "key": PLACES_API_KEY,
    }
    places_response = requests.get(places_url, params=places_params)

    if places_response.status_code != 200:
        return jsonify({"error": "Places API error"}), places_response.status_code

    places_data = places_response.json()
    top_places = [
        {
            "name": place["name"],
            "address": place.get("vicinity", "No address available"),
            "rating": place.get("rating", "No rating available"),
            "user_ratings_total": place.get("user_ratings_total", 0),
            "types": place.get("types", []),
        }
        for place in places_data.get("results", [])
    ]

    recommended_places, recommendation_message = recommend_places(top_places, weather_condition)
    
    response_data = {
        "city": city,
        "weather": {
            "temperature": weather_data["main"]["temp"],
            "condition": weather_condition,
        },
        "city_info": city_info,
        "recommended_places": recommended_places,
        "recommendation_message": recommendation_message or "Here are the top tourist places to visit.",
    }

    model.add_city_info({
        "city": city,
        "weather": f"{weather_data['main']['temp']}°C, {weather_condition}",
        "recommendations": ", ".join([place["name"] for place in recommended_places])
    })

    return jsonify(response_data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Use the PORT environment variable or default to 8080
    app.run(host="0.0.0.0", port=port, debug=True)

