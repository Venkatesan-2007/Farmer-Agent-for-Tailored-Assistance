# ai_farm_assistant.py (FINAL VERSION)
# ✅ Unified Streamlit App with Kisan Card Verification, Login, AI Chat, Crop Advice, Voice Bot, Weather, Soil Logs, Rentals

import streamlit as st
import os
import json
import hashlib
import joblib
import pandas as pd
import requests
from PIL import Image
import pyttsx3
import speech_recognition as sr
from sklearn.ensemble import RandomForestClassifier
import time

# --- API KEYS ---
OPENROUTER_API_KEY = "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"
WEATHER_API_KEY = "d24618da5731a22860858819d5aaf0d3"

# --- Kisan Card Verification ---
def show_kisan_verification():
    st.title("🌾 Kisan Card Verification")
    code = st.text_input("Enter 12 Digit Kisan Card Number", max_chars=12)
    if st.button("Verify Kisan Card"):
        if code == "123456789123":
            st.success("✔ Kisan Card Verified Successfully")
            st.balloons()
            time.sleep(2)
            return True
        else:
            st.error("❌ Invalid Kisan Card Number")
            return False
    return False

# --- AI Chat Call ---
def ask_openrouter(prompt, system_msg="You are an agricultural assistant"):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openai/gpt-4",
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        res = requests.post(url, headers=headers, data=json.dumps(payload))
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"AI Error: {str(e)}"

# --- Weather Fetch ---
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    try:
        r = requests.get(url)
        d = r.json()
        if d.get("cod") != 200:
            return None, d.get("message")
        rain = d.get("rain", {}).get("1h", 0.0)
        return {
            "temperature": d["main"]["temp"],
            "humidity": d["main"]["humidity"],
            "wind_speed": d["wind"]["speed"] * 3.6,
            "sky": d["weather"][0]["main"],
            "rainfall": rain
        }, None
    except Exception as e:
        return None, str(e)

# --- Text-to-Speech ---
engine = pyttsx3.init()
def speak(text):
    engine.say(text)
    engine.runAndWait()

# --- Speech Recognition ---
def recognize_voice():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening...")
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except:
        return "Sorry, couldn't understand."

# --- Image Disease Detector (Mock) ---
def detect_disease(image):
    st.image(image, caption="Leaf Uploaded")
    return "🦠 Diagnosis: Leaf appears to be affected by Early Blight."

# --- Utility: Hashing Password ---
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

# --- User + Profile Management ---
def load_users():
    return json.load(open("users.json")) if os.path.exists("users.json") else {}

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

# --- ML Crop Recommendation Model ---
def train_crop_model():
    df = pd.DataFrame({
        "N": [90, 40, 60, 80],
        "P": [40, 35, 50, 60],
        "K": [40, 60, 70, 80],
        "temperature": [21, 23, 25, 28],
        "humidity": [80, 65, 75, 60],
        "ph": [6.5, 7.0, 6.2, 6.8],
        "rainfall": [200, 150, 180, 210],
        "label": ["tomato", "chili", "tomato", "onion"]
    })
    X, y = df.drop("label", axis=1), df["label"]
    model = RandomForestClassifier().fit(X, y)
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/crop_model.pkl")
    return model

model = joblib.load("models/crop_model.pkl") if os.path.exists("models/crop_model.pkl") else train_crop_model()

# --- Streamlit App Start ---
st.set_page_config(page_title="🌾 AI Farmer Assistant", layout="wide")

# --- Kisan Card Screen ---
if "kisan_verified" not in st.session_state:
    st.session_state.kisan_verified = False

if not st.session_state.kisan_verified:
    if show_kisan_verification():
        st.session_state.kisan_verified = True
    st.stop()

# --- Session Init ---
def init_session():
    for key in ["logged_in", "username", "role", "soil_data", "chat", "rental_data"]:
        if key not in st.session_state:
            st.session_state[key] = [] if key in ["soil_data", "chat", "rental_data"] else ""
init_session()

# --- Login or Register ---
if not st.session_state.logged_in:
    st.header("🔐 Login or Register")
    users = load_users()
    choice = st.radio("Choose Option", ["Login", "Register"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if choice == "Register":
        confirm = st.text_input("Confirm Password", type="password")
        role = st.selectbox("Role", ["Buyer", "Seller"])
        if st.button("Register"):
            if username in users:
                st.error("Username exists.")
            elif password != confirm:
                st.error("Passwords do not match.")
            else:
                users[username] = {"password": hash_password(password), "role": role.lower()}
                save_users(users)
                st.success("Registered successfully.")
    else:
        if st.button("Login"):
            if username in users and users[username]["password"] == hash_password(password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = users[username]["role"]
            else:
                st.error("Invalid login.")
    st.stop()

# --- Main Navigation ---
menu = st.sidebar.selectbox("📚 Menu", ["Home", "Crop Advice", "Chat AI", "Voice Bot", "Disease Check", "Soil Logs", "Rentals", "Logout"])

if menu == "Home":
    st.title(f"Welcome, {st.session_state.username.title()} ({st.session_state.role.title()})")
    st.info("Explore weather-based crop advice, disease detection, AI chat, soil logs and rentals.")

elif menu == "Crop Advice":
    st.header("🌱 Crop Advice")
    col1, col2 = st.columns(2)
    with col1:
        city = st.text_input("📍 City")
        soil = st.selectbox("🧪 Soil Type", ["Sandy", "Loamy", "Clay", "Silty", "Peaty", "Chalky"])
    with col2:
        crop = st.text_input("🌾 Crop (e.g., Tomato, Paddy)")

    if st.button("🌦️ Get Advice") and city and crop:
        weather, err = get_weather(city)
        if err:
            st.error(err)
        else:
            st.markdown(f"""
            - Temp: `{weather['temperature']} °C`
            - Humidity: `{weather['humidity']}%`
            - Wind: `{weather['wind_speed']:.1f} km/h`
            - Sky: `{weather['sky']}`
            - Rain: `{weather['rainfall']} mm`
            """)
            prompt = f"I am in {city}. I want to plant {crop} in {soil} soil. Temp: {weather['temperature']} C. Humidity: {weather['humidity']}%. Rain: {weather['rainfall']}mm. Is it a good day to plant?"
            result = ask_openrouter(prompt)
            st.success(result)

elif menu == "Chat AI":
    st.header("💬 Chat with AI")
    q = st.text_input("Ask a question")
    if st.button("Ask") and q:
        r = ask_openrouter(q)
        st.success(r)
        speak(r)

elif menu == "Voice Bot":
    st.header("🎤 Voice Input")
    if st.button("🎙️ Listen"):
        voice = recognize_voice()
        st.info(f"You said: {voice}")
        res = ask_openrouter(voice)
        st.success(res)
        speak(res)

elif menu == "Disease Check":
    st.header("🧪 Leaf Detection (Mock)")
    f = st.file_uploader("Upload Leaf Image", type=["jpg", "png"])
    if f:
        img = Image.open(f)
        msg = detect_disease(img)
        st.success(msg)
        speak(msg)

elif menu == "Soil Logs":
    st.header("🧪 Log Soil Parameters")
    pH = st.number_input("pH", 0.0, 14.0)
    m = st.slider("Moisture", 0, 100)
    N = st.number_input("N")
    P = st.number_input("P")
    K = st.number_input("K")
    if st.button("Save Soil Data"):
        st.session_state.soil_data.append({"pH": pH, "Moisture": m, "N": N, "P": P, "K": K})
        st.success("Saved.")
    if st.session_state.soil_data:
        st.dataframe(pd.DataFrame(st.session_state.soil_data))

elif menu == "Rentals":
    st.header("🚜 Equipment Rentals")
    eq = st.text_input("Equipment")
    owner = st.text_input("Owner")
    loc = st.text_input("Location")
    mob = st.text_input("Mobile")
    if st.button("Add Rental") and eq and mob:
        st.session_state.rental_data.append({"Equipment": eq, "Owner": owner, "Location": loc, "Mobile": mob})
        st.success("Added.")
    if st.session_state.rental_data:
        st.dataframe(pd.DataFrame(st.session_state.rental_data))

elif menu == "Logout":
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.success("Logged out. Refresh to restart.")
