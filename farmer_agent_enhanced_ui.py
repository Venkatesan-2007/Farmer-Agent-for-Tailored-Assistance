
# 🌿 FARMER AGENT APP – Enhanced UI/UX
import os
import json
import numpy as np
import pandas as pd
import streamlit as st
import joblib
import pyttsx3
import speech_recognition as sr
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# -------------------------
# Streamlit Setup
# -------------------------
st.set_page_config(page_title="🌾 Farmer Agent Assistant", layout="wide")
st.markdown("<h1 style='text-align: center; color: green;'>🌾 AI-Powered Farmer Agent</h1>", unsafe_allow_html=True)

# -------------------------
# Load or Train Crop Model
# -------------------------
def train_crop_model():
    data = {
        "N": [90, 40, 60, 80],
        "P": [40, 35, 50, 60],
        "K": [40, 60, 70, 80],
        "temperature": [21, 23, 25, 28],
        "humidity": [80, 65, 75, 60],
        "ph": [6.5, 7.0, 6.2, 6.8],
        "rainfall": [200, 150, 180, 210],
        "label": ["tomato", "chili", "tomato", "onion"]
    }
    df = pd.DataFrame(data)
    X = df.drop("label", axis=1)
    y = df["label"]
    model = RandomForestClassifier()
    model.fit(X, y)
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/crop_model.pkl")
    return model

model_path = "models/crop_model.pkl"
if os.path.exists(model_path):
    crop_model = joblib.load(model_path)
else:
    crop_model = train_crop_model()

# -------------------------
# Market Data
# -------------------------
market_data = {
    "Tomato": {
        "Dindigul": "₹28/kg",
        "Madurai": "₹26/kg",
        "Salem": "₹30/kg",
        "Coimbatore": "₹27/kg",
        "Trichy": "₹29/kg"
    },
    "Onion": {
        "Madurai": "₹18/kg",
        "Salem": "₹20/kg"
    }
}

# -------------------------
# Assistant Functions
# -------------------------
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def listen_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Listening...")
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Sorry, I could not understand."
    except sr.RequestError:
        return "Sorry, service is unavailable."

class Assistant:
    def get_fertilizer_tips(self, stage):
        tips = {
            "Pre-Planting": "Add compost and plow soil well.",
            "Growing": "Apply nitrogen-rich fertilizer every 15 days.",
            "Flowering": "Use phosphorous and potassium mix.",
        }
        return tips.get(stage, "No specific tips for that stage.")

    def get_crop_variety(self, soil_type, season):
        if soil_type == "Red Loamy Soil" and season == "Kharif":
            return ["PKM-1", "Arka Vikas", "Sankranthi"]
        return ["Variety A", "Variety B"]

    def get_weather_forecast(self, location):
        return [
            {"day": "Monday", "forecast": "☀️ Sunny"},
            {"day": "Tuesday", "forecast": "⛅ Cloudy"},
            {"day": "Wednesday", "forecast": "🌧️ Rain"},
            {"day": "Thursday", "forecast": "☀️ Sunny"},
            {"day": "Friday", "forecast": "🌧️ Rain"},
            {"day": "Saturday", "forecast": "💨 Windy"},
            {"day": "Sunday", "forecast": "☀️ Sunny"},
        ]

    def get_market_prices(self):
        return market_data

assistant = Assistant()

# -------------------------
# Layout Columns
# -------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🌱 Best Crop Varieties")
    if st.button("🔍 Show Varieties"):
        varieties = assistant.get_crop_variety("Red Loamy Soil", "Kharif")
        st.success("Recommended Varieties: " + ", ".join(varieties))

    st.markdown("### 🌦️ Weekly Weather Forecast")
    if st.button("📆 Show Forecast"):
        forecast = assistant.get_weather_forecast("Kodaikanal")
        for day in forecast:
            st.write(f"**{day['day']}**: {day['forecast']}")

with col2:
    st.markdown("### 🧺 Market Price Overview")
    if st.button("📊 Show Market Prices"):
        prices = assistant.get_market_prices()
        for crop, city_prices in prices.items():
            st.markdown(f"<h5 style='color:#4CAF50;'>{crop}</h5>", unsafe_allow_html=True)
            cols = st.columns(2)
            for i, (city, price) in enumerate(city_prices.items()):
                with cols[i % 2]:
                    st.info(f"**{city}**: {price}")

# -------------------------
# Voice Interaction
# -------------------------
st.markdown("### 🎤 Voice Command")
if st.button("🎙️ Start Listening"):
    query = listen_command()
    st.write("You said:", query)
    response = assistant.get_fertilizer_tips("Pre-Planting")
    st.success("🧠 Assistant: " + response)
    speak(response)
