import streamlit as st
import openai
import requests

# --- 🔐 Secret Keys (Replace with st.secrets when deployed) ---
openai.api_key = "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"  # Replace securely
weather_api_key = "d24618da5731a22860858819d5aaf0d3"

# --- 🌐 OpenWeather API Function ---
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()
        if data.get("cod") != 200:
            return None, data.get("message", "Failed to get weather.")
        weather = {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"] * 3.6,  # Convert m/s to km/h
            "sky": data["weather"][0]["main"]
        }
        return weather, None
    except Exception as e:
        return None, str(e)

# --- 🖼️ Streamlit UI ---
st.set_page_config(page_title="👨‍🌾 AI Farming Assistant", layout="centered")
st.title("👨‍🌾 AI-Powered Farming Assistant")
st.markdown("Enter a location to get live weather and smart farming suggestions.")

# --- 📍 User Input ---
location = st.text_input("📍 Enter City Name", "")

if st.button("🌦️ Get Live Weather & Farming Advice"):
    if not location:
        st.warning("Please enter a city name.")
    else:
        st.info("Fetching live weather data...")
        weather, error = get_weather(location)

        if error:
            st.error(f"⚠️ Error: {error}")
        else:
            # Display weather
            st.success("✅ Live Weather:")
            st.markdown(f"""
            - 🌡️ Temperature: `{weather['temperature']} °C`  
            - 💧 Humidity: `{weather['humidity']}%`  
            - 💨 Wind Speed: `{weather['wind_speed']:.1f} km/h`  
            - ☁️ Sky Condition: `{weather['sky']}`
            """)

            # --- 🤖 Build prompt for AI ---
            prompt = f"""
            Based on the following live weather in {location}, suggest farming activities suitable for today.

            - Temperature: {weather['temperature']} °C
            - Humidity: {weather['humidity']} %
            - Wind Speed: {weather['wind_speed']:.1f} km/h
            - Sky Condition: {weather['sky']}

            Provide practical advice for farmers including seed planting, irrigation, or precautions.
            """

            with st.spinner("Generating farming advice using AI..."):
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4",  # or gpt-3.5-turbo
                        messages=[
                            {"role": "system", "content": "You are an agricultural expert giving smart advice to farmers."},
                            {"role": "user", "content": prompt}
                        ]
                    )
                    advice = response["choices"][0]["message"]["content"]
                    st.success("🧠 Smart Farming Advice:")
                    st.markdown(advice)
                except Exception as e:
                    st.error(f"⚠️ AI Error: {str(e)}")
