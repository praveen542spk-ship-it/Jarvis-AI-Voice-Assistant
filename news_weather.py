"""
news_weather.py — Real-time News + Weather for Jarvis
APIs: NewsAPI.org + OpenWeatherMap
Location: Auto-detect via IP — no hardcode city needed!
"""
import requests
import os

# ─────────────────────────────────────────────────────────────
#  API KEYS — Loaded dynamically from local untracked files
# ─────────────────────────────────────────────────────────────
NEWS_API_KEY    = ""
WEATHER_API_KEY = ""

NEWS_KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "news_key.txt")
if os.path.exists(NEWS_KEY_FILE):
    try:
        with open(NEWS_KEY_FILE, "r", encoding="utf-8") as f:
            NEWS_API_KEY = f.read().strip()
    except Exception as e:
        print(f"[News Key Load Error] {e}")

WEATHER_KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "weather_key.txt")
if os.path.exists(WEATHER_KEY_FILE):
    try:
        with open(WEATHER_KEY_FILE, "r", encoding="utf-8") as f:
            WEATHER_API_KEY = f.read().strip()
    except Exception as e:
        print(f"[Weather Key Load Error] {e}")

if not NEWS_API_KEY:
    NEWS_API_KEY = "PLACEHOLDER_NEWS_KEY"
if not WEATHER_API_KEY:
    WEATHER_API_KEY = "PLACEHOLDER_WEATHER_KEY"

# ─────────────────────────────────────────────────────────────
#  AUTO LOCATION DETECT
# ─────────────────────────────────────────────────────────────
def get_current_location():
    """
    IP address வழியா current city + country auto detect பண்ணும்.
    Internet இருந்தா always correct city கிடைக்கும்.
    No GPS, no hardcode needed!
    """
    try:
        # Free IP geolocation API — no key needed
        response = requests.get("http://ip-api.com/json/", timeout=5)
        data     = response.json()
        if data.get("status") == "success":
            city    = data.get("city", "Chennai")
            country = data.get("countryCode", "IN")
            lat     = data.get("lat")
            lon     = data.get("lon")
            print(f"[Location] Detected: {city}, {country}")
            return city, country, lat, lon
    except Exception as e:
        print(f"[Location Error] {e}")

    # Fallback
    return "Chennai", "IN", 13.08, 80.27


# ─────────────────────────────────────────────────────────────
#  WEATHER
# ─────────────────────────────────────────────────────────────
def get_weather(city=None):
    """
    city=None → auto detect current location
    city="Mumbai" → that city weather
    Returns speak-ready string.
    """
    try:
        # City இல்லன்னா auto detect
        if city is None:
            city, country, lat, lon = get_current_location()

        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q":     city,
            "appid": WEATHER_API_KEY,
            "units": "metric",
        }
        response = requests.get(url, params=params, timeout=8)
        data     = response.json()

        if data.get("cod") != 200:
            msg = data.get("message", "Unknown error")
            return f"Sorry, I could not get weather for {city}. {msg}"

        temp       = round(data["main"]["temp"])
        feels_like = round(data["main"]["feels_like"])
        humidity   = data["main"]["humidity"]
        condition  = data["weather"][0]["description"].capitalize()
        city_name  = data["name"]
        country    = data["sys"]["country"]
        wind_speed = round(data["wind"]["speed"] * 3.6)

        # High/low
        temp_max = round(data["main"]["temp_max"])
        temp_min = round(data["main"]["temp_min"])

        result = (
            f"Current weather in {city_name}, {country}. "
            f"Temperature is {temp} degrees Celsius. "
            f"Feels like {feels_like} degrees. "
            f"Today's high is {temp_max} and low is {temp_min} degrees. "
            f"Condition: {condition}. "
            f"Humidity: {humidity} percent. "
            f"Wind speed: {wind_speed} kilometers per hour."
        )
        return result

    except requests.exceptions.ConnectionError:
        return "No internet connection. Cannot fetch weather."
    except requests.exceptions.Timeout:
        return "Weather request timed out. Please try again."
    except Exception as e:
        print(f"[Weather Error] {e}")
        return "Sorry, something went wrong fetching weather."


# ─────────────────────────────────────────────────────────────
#  NEWS
# ─────────────────────────────────────────────────────────────
def get_news(category="general", country="in", count=3):
    """
    Latest headlines fetch பண்ணும்.
    country auto-detect location-க்கு ஏத்தமாதிரி set ஆகும்.
    """
    try:
        # Country auto detect
        _, detected_country, _, _ = get_current_location()
        country = detected_country.lower()

        # NewsAPI country codes support பண்றவை
        supported = ["us", "gb", "in", "au", "ca", "de", "fr", "jp"]
        if country not in supported:
            country = "in"   # Default India

        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "apiKey":   NEWS_API_KEY,
            "country":  country,
            "category": category,
            "pageSize": count,
        }
        response = requests.get(url, params=params, timeout=8)
        data     = response.json()

        if data.get("status") != "ok":
            return ["Sorry, I could not fetch news right now."]

        articles = data.get("articles", [])
        if not articles:
            return ["No news found for this category."]

        headlines = []
        for i, article in enumerate(articles[:count], 1):
            title  = article.get("title", "No title")
            source = article.get("source", {}).get("name", "")
            if " - " in title:
                title = title.rsplit(" - ", 1)[0]
            headlines.append(f"Headline {i}: {title}. Source: {source}.")

        return headlines

    except requests.exceptions.ConnectionError:
        return ["No internet connection. Cannot fetch news."]
    except requests.exceptions.Timeout:
        return ["News request timed out. Please try again."]
    except Exception as e:
        print(f"[News Error] {e}")
        return ["Sorry, something went wrong fetching news."]


def speak_news(category="general"):
    """News headlines speak-ready string-ஆ return பண்ணும்."""
    headlines = get_news(category=category)
    intro     = f"Here are the latest {category} news headlines. "
    return intro + " ".join(headlines)


# ─────────────────────────────────────────────────────────────
#  TEST
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":

    print("\n[1] Internet check...")
    try:
        r = requests.get("https://www.google.com", timeout=5)
        print(f"    ✅ Internet OK — {r.status_code}")
    except Exception as e:
        print(f"    ❌ {e}")

    print("\n[2] Location detect...")
    city, country, lat, lon = get_current_location()
    print(f"    City: {city} | Country: {country}")

    print("\n[3] Weather API...")
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        r = requests.get(url, params={"q":"London","appid":WEATHER_API_KEY,"units":"metric"}, timeout=8)
        data = r.json()
        print(f"    HTTP: {r.status_code} | cod: {data.get('cod')} | msg: {data.get('message','ok')}")
        if data.get('cod') == 200:
            print(f"    ✅ Weather working! Temp: {data['main']['temp']}C")
        elif data.get('cod') == 401:
            print("    ❌ Invalid key or not activated yet (wait 10 mins)")
    except Exception as e:
        print(f"    ❌ {e}")

    print("\n[4] News API...")
    try:
        url = "https://newsapi.org/v2/top-headlines"
        r = requests.get(url, params={"apiKey":NEWS_API_KEY,"country":"in","pageSize":1}, timeout=8)
        data = r.json()
        print(f"    HTTP: {r.status_code} | status: {data.get('status')} | msg: {data.get('message','ok')}")
        if data.get('status') == 'ok':
            print("    ✅ News working!")
        else:
            print("    ❌ Error")
    except Exception as e:
        print(f"    ❌ {e}")