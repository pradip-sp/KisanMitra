import os
import requests
from django.shortcuts import render

# ---------------------------------------------------------------------------
# WeatherAPI.com configuration
# Get a free key at https://www.weatherapi.com/signup.aspx
# Best practice: set it as an environment variable instead of hardcoding it.
#   export WEATHERAPI_KEY="your_key_here"        (Linux/Mac)
#   setx WEATHERAPI_KEY "your_key_here"           (Windows)
# ---------------------------------------------------------------------------
WEATHERAPI_KEY = os.environ.get("WEATHERAPI_KEY", "PUT_YOUR_API_KEY_HERE")

SEARCH_URL = "https://api.weatherapi.com/v1/search.json"
FORECAST_URL = "https://api.weatherapi.com/v1/forecast.json"


def search_cities(city_name):
    """Return matching locations for a city name search (for disambiguation)."""
    params = {"key": WEATHERAPI_KEY, "q": city_name}
    resp = requests.get(SEARCH_URL, params=params, timeout=8)
    resp.raise_for_status()
    results = resp.json() or []
    matches = []
    for r in results:
        matches.append({
            "name": r.get("name"),
            "region": r.get("region"),
            "country": r.get("country"),
            "latitude": r.get("lat"),
            "longitude": r.get("lon"),
        })
    return matches


def fetch_weather(query):
    """
    Fetch current + hourly + 6-day forecast (with rain probability) from WeatherAPI.com.
    `query` can be a city name, or "lat,lon" string.
    """
    params = {
        "key": WEATHERAPI_KEY,
        "q": query,
        "days": 6,
        "aqi": "no",
        "alerts": "no",
    }
    resp = requests.get(FORECAST_URL, params=params, timeout=8)
    resp.raise_for_status()
    return resp.json()


def build_weather_context(raw):
    """Shape the raw WeatherAPI.com response into what the template expects."""
    loc = raw.get("location", {})
    location = {
        "name": loc.get("name"),
        "region": loc.get("region"),
        "country": loc.get("country"),
        "latitude": loc.get("lat"),
        "longitude": loc.get("lon"),
    }

    cur = raw.get("current", {})
    condition = cur.get("condition", {}) or {}
    current = {
        "temperature": cur.get("temp_c"),
        "feels_like": cur.get("feelslike_c"),
        "humidity": cur.get("humidity"),
        "wind_speed": cur.get("wind_kph"),
        "pressure": cur.get("pressure_mb"),
        "description": condition.get("text"),
        "icon": condition.get("icon"),
        "is_day": cur.get("is_day") == 1,
    }

    forecast_days = raw.get("forecast", {}).get("forecastday", [])

    daily_forecast = []
    for fd in forecast_days:
        day = fd.get("day", {})
        astro = fd.get("astro", {})
        d_condition = day.get("condition", {}) or {}
        daily_forecast.append({
            "date": fd.get("date"),
            "max_temp": day.get("maxtemp_c"),
            "min_temp": day.get("mintemp_c"),
            "rain_chance": day.get("daily_chance_of_rain"),
            "description": d_condition.get("text"),
            "icon": d_condition.get("icon"),
            "sunrise": astro.get("sunrise"),
            "sunset": astro.get("sunset"),
        })

    # Hourly forecast for the next 24 hours: today's remaining hours + tomorrow's early hours
    hourly_forecast = []
    for fd in forecast_days[:2]:
        for h in fd.get("hour", []):
            hourly_forecast.append(h)
    hourly_forecast = hourly_forecast[:24]

    hourly = []
    for h in hourly_forecast:
        h_condition = h.get("condition", {}) or {}
        time_str = h.get("time", "")  # "2026-08-13 14:00"
        clock = time_str.split(" ")[-1] if " " in time_str else time_str
        hourly.append({
            "time": clock,
            "temp": h.get("temp_c"),
            "rain_chance": h.get("chance_of_rain"),
            "icon": h_condition.get("icon"),
            "description": h_condition.get("text"),
        })

    return location, current, daily_forecast, hourly


def weather_page(request):
    city_query = request.GET.get("city", "")
    lat_param = request.GET.get("lat")
    lon_param = request.GET.get("lon")

    error = None
    location = None
    current = None
    daily_forecast = []
    hourly_forecast = []
    options = []  # multiple matches for the user to pick from

    if WEATHERAPI_KEY == "PUT_YOUR_API_KEY_HERE":
        error = (
            "WeatherAPI.com key set nahi hai. views.py mein WEATHERAPI_KEY set karein, "
            "ya WEATHERAPI_KEY environment variable use karein."
        )
        return render(request, "weather.html", {"error": error})

    try:
        if lat_param and lon_param:
            # Came from the "Use my location" browser button
            raw = fetch_weather(f"{lat_param},{lon_param}")
            location, current, daily_forecast, hourly_forecast = build_weather_context(raw)

        elif city_query:
            matches = search_cities(city_query)
            if not matches:
                error = f'"{city_query}" ke liye koi location nahi mili. Sahi shehar ka naam try karein.'
            elif len(matches) == 1:
                m = matches[0]
                raw = fetch_weather(f"{m['latitude']},{m['longitude']}")
                location, current, daily_forecast, hourly_forecast = build_weather_context(raw)
            else:
                # Multiple cities with the same/similar name -> let user choose
                options = matches

        else:
            # Nothing searched yet, nothing selected — default city
            raw = fetch_weather("Varanasi")
            location, current, daily_forecast, hourly_forecast = build_weather_context(raw)

    except requests.RequestException:
        error = "Weather data laane mein problem hui. API key check karein ya thodi der baad try karein."

    context = {
        "city_query": city_query,
        "location": location,
        "current": current,
        "daily_forecast": daily_forecast,
        "hourly_forecast": hourly_forecast,
        "error": error,
        "options": options,
    }
    return render(request, "weather.html", context)