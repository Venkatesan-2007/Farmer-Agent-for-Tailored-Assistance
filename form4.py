import streamlit as st
import os
import json
import hashlib
import joblib
import numpy as np
import pandas as pd
import pyttsx3
import speech_recognition as sr
from sklearn.ensemble import RandomForestClassifier

# Streamlit setup
st.set_page_config(page_title="🌾 Farmer Agent App", layout="wide")
st.markdown("<h1 style='text-align: center; color: green;'>🌾 Farmer Agent Portal</h1>", unsafe_allow_html=True)

# ==========================
# User & Profile Functions
# ==========================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

def save_profile(username, info):
    os.makedirs("profiles", exist_ok=True)
    with open(f"profiles/{username}.json", "w") as f:
        json.dump(info, f, indent=4)

def load_profile(username):
    try:
        with open(f"profiles/{username}.json", "r") as f:
            return json.load(f)
    except:
        return {}

# ==========================
# Session Initialization
# ==========================
for key in ["logged_in", "username", "profile_updated", "show_home"]:
    if key not in st.session_state:
        st.session_state[key] = False if key != "username" else ""

# ==========================
# Auth Interface
# ==========================
if not st.session_state["logged_in"] and not st.session_state["show_home"]:
    users = load_users()
    auth_mode = st.radio("Select Option", ["Sign In", "Sign Up"], horizontal=True, key="auth_mode")
    username = st.text_input("Username", key="auth_user")
    password = st.text_input("Password", type="password", key="auth_pass")

    if auth_mode == "Sign Up":
        confirm_password = st.text_input("Confirm Password", type="password", key="auth_confirm")
        if st.button("Register", key="register_btn"):
            if username in users:
                st.error("Username already exists.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            elif not username or not password:
                st.warning("Please fill in all fields.")
            else:
                users[username] = hash_password(password)
                save_users(users)
                st.success("✅ Account created. Please sign in.")

    elif auth_mode == "Sign In":
        if st.button("Login", key="login_btn"):
            if username in users and users[username] == hash_password(password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"✅ Welcome, {username}!")
            else:
                st.error("❌ Invalid username or password.")

# ==========================
# Profile & Redirect
# ==========================
if st.session_state.logged_in and not st.session_state.show_home:
    st.markdown("---")
    st.header("👤 Profile Info")
    profile = load_profile(st.session_state.username)
    uploaded_file = st.file_uploader("Upload Profile Picture", type=["jpg", "png", "jpeg"])
    name = st.text_input("Full Name", profile.get("name", ""), key="name")
    email = st.text_input("Email", profile.get("email", ""), key="email")
    location = st.text_input("Location", profile.get("location", ""), key="location")

    if st.button("📏 Save Profile"):
        save_profile(st.session_state.username, {
            "name": name, "email": email, "location": location
        })

        if uploaded_file:
            os.makedirs("profile_pics", exist_ok=True)
            with open(f"profile_pics/{st.session_state.username}.jpg", "wb") as f:
                f.write(uploaded_file.read())

        st.session_state.profile_updated = True
        st.session_state.show_home = True
        st.success("✅ Profile updated. Redirecting to home page...")
        st.rerun()

    if st.session_state.profile_updated:
        st.session_state.profile_updated = False

    pic_path = f"profile_pics/{st.session_state.username}.jpg"
    if os.path.exists(pic_path):
        st.image(pic_path, width=150, caption="Your Profile Picture")

    st.markdown("---")
    if st.button("🚪 Logout", key="logout_from_profile"):
        for key in ["logged_in", "username", "profile_updated", "show_home"]:
            st.session_state[key] = False if key != "username" else ""
        st.rerun()

# ==========================
# Main Home Page
# ==========================
if st.session_state.show_home:
    st.title("🌿 Farmer Agent AI Assistant")

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
    crop_model = joblib.load(model_path) if os.path.exists(model_path) else train_crop_model()

    market_data = {
        "Tomato": {
            "Dindigul": "₹28/kg", "Madurai": "₹26/kg", "Salem": "₹30/kg",
            "Coimbatore": "₹27/kg", "Trichy": "₹29/kg"
        },
        "Onion": {
            "Madurai": "₹18/kg", "Salem": "₹20/kg"
        }
    }

    def speak(text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    def listen_command():
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("🎤 Listening...")
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
                {"day": "Saturday", "forecast": "🌬️ Windy"},
                {"day": "Sunday", "forecast": "☀️ Sunny"},
            ]

        def get_market_prices(self):
            return market_data

    assistant = Assistant()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🌱 Best Crop Varieties")
        if st.button("🔍 Show Varieties"):
            varieties = assistant.get_crop_variety("Red Loamy Soil", "Kharif")
            st.success("Recommended Varieties: " + ", ".join(varieties))

        st.markdown("### 🌦️ Weekly Weather Forecast")
        if st.button("🗖️ Show Forecast"):
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

    st.markdown("### 🎤 Voice Command")
    if st.button("🎤 Start Listening"):
        query = listen_command()
        st.write("You said:", query)
        response = assistant.get_fertilizer_tips("Pre-Planting")
        st.success("🧠 Assistant: " + response)
        speak(response)

    st.markdown("---")
    if st.button("🚪 Logout", key="logout_home"):
        for key in ["logged_in", "username", "profile_updated", "show_home"]:
            st.session_state[key] = False if key != "username" else ""
        st.rerun()
