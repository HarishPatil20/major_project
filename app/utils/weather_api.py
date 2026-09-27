import os
import requests
import streamlit as st
from dotenv import load_dotenv

# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv(
    dotenv_path=os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        ".env"
    )
)

API_KEY = os.getenv("OPENWEATHER_API_KEY")

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


# =========================================================
# GET WEATHER
# =========================================================

@st.cache_data(ttl=600, show_spinner=False)
def get_weather(city: str = "", latitude: float = None, longitude: float = None) -> dict:

    has_coordinates = latitude is not None and longitude is not None

    if not has_coordinates and (not city or not city.strip()):
        return {
            "success": False,
            "message": "Location is required to load weather."
        }

    if not API_KEY:
        return {
            "success": False,
            "message": "OpenWeather API key is missing. Please check your .env file."
        }

    params = {
        "appid": API_KEY,
        "units": "metric"
    }

    if has_coordinates:
        params.update({"lat": latitude, "lon": longitude})
    else:
        params["q"] = city.strip()

    try:

        response = requests.get(
            BASE_URL,
            params=params,
            timeout=10
        )

    except requests.exceptions.Timeout:

        return {
            "success": False,
            "message": "Weather service timed out. Please try again."
        }

    except requests.exceptions.ConnectionError:

        return {
            "success": False,
            "message": "Unable to connect to OpenWeather. Please check your internet connection."
        }

    except requests.exceptions.RequestException as e:

        return {
            "success": False,
            "message": f"Network error: {e}"
        }

    # =====================================================
    # API ERRORS
    # =====================================================

    if response.status_code == 401:

        return {
            "success": False,
            "message": "Invalid OpenWeather API key."
        }

    if response.status_code == 404:

        return {
            "success": False,
            "message": "Weather could not be found for your current location."
        }

    if response.status_code != 200:

        try:
            data = response.json()
            message = data.get(
                "message",
                f"Weather service error: {response.status_code}"
            )
        except Exception:
            message = (
                f"Weather service error: "
                f"{response.status_code}"
            )

        return {
            "success": False,
            "message": message
        }

    # =====================================================
    # PROCESS WEATHER DATA
    # =====================================================

    try:

        data = response.json()

        weather = data.get("weather", [{}])[0]
        main = data.get("main", {})
        wind = data.get("wind", {})
        coord = data.get("coord", {})
        system = data.get("sys", {})

        latitude = coord.get("lat")
        longitude = coord.get("lon")

        if latitude is None or longitude is None:

            return {
                "success": False,
                "message": "Weather data received but location coordinates are missing."
            }

        return {

            "success": True,

            "city": data.get(
                "name",
                city.strip()
            ),

            "country": system.get(
                "country",
                ""
            ),

            "temperature": round(
                float(main.get("temp", 0)),
                1
            ),

            "feels_like": round(
                float(main.get("feels_like", 0)),
                1
            ),

            "humidity": int(
                main.get("humidity", 0)
            ),

            "pressure": int(
                main.get("pressure", 0)
            ),

            "wind_speed": round(
                float(wind.get("speed", 0)),
                1
            ),

            "condition": weather.get(
                "main",
                "Unknown"
            ),

            "description": weather.get(
                "description",
                ""
            ),

            "icon": weather.get(
                "icon",
                "01d"
            ),

            "latitude": float(latitude),

            "longitude": float(longitude)
        }

    except (ValueError, TypeError, KeyError, IndexError) as e:

        return {
            "success": False,
            "message": f"Invalid weather data received: {e}"
        }

    except Exception as e:

        return {
            "success": False,
            "message": f"Unexpected weather error: {e}"
        }


@st.cache_data(ttl=300, show_spinner=False)
def get_auto_location(browser_location=None):
    """
    Resolves location coordinates:
    1. HTML5 Browser Geolocation (if provided)
    2. IP-based Geolocation (via ip-api.com)
    3. Default Fallback: Mangalore / Mangaluru (12.9141, 74.8560)

    NOTE: this used to run with no caching at all, which meant every
    single page rerun (every button click, every navigation back to the
    Dashboard/Weather page, since the whole page script re-executes each
    time) made a fresh blocking network call to ip-api.com whenever the
    browser hadn't granted GPS permission yet - adding up to ~3 extra
    seconds to *every* rerun, not just the first page load. Caching this
    for 5 minutes means that IP lookup now happens at most once every 5
    minutes instead of on every single interaction, which is one of the
    main causes of the app feeling slow when moving between pages.
    """
    if browser_location and isinstance(browser_location, dict):
        lat = browser_location.get("latitude")
        lon = browser_location.get("longitude")
        if lat is not None and lon is not None:
            return float(lat), float(lon), "Browser GPS"

    try:
        resp = requests.get("http://ip-api.com/json/", timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "success":
                lat = data.get("lat")
                lon = data.get("lon")
                city = data.get("city", "Mangalore")
                if lat is not None and lon is not None:
                    return float(lat), float(lon), f"Auto-Detected ({city})"
    except Exception:
        pass

    return 12.9141, 74.8560, "Mangalore (Default)"