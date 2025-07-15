import streamlit as st
import os
import json
import hashlib
import pandas as pd
import joblib
import pyttsx3
import speech_recognition as sr
import google.generativeai as genai
from sklearn.ensemble import RandomForestClassifier
from dotenv import load_dotenv

# Load Gemini API Key from .env
load_dotenv()
api_key = os.getenv("AIzaSyBC_biuzwttea4iIpgi4sFFWRjD00Kx4EU")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-pro")

# ---------- Streamlit Page Setup ----------
st.set_page_config(page_title="🌾 Farmer Assistant App", layout="wide")

# ---------- Utility Functions ----------
def hash_password(password): return hashlib.sha256(password.encode()).hexdigest()

def load_users(): return json.load(open("users.json")) if os.path.exists("users.json") else {}

def save_users(users): json.dump(users, open("users.json", "w"), indent=4)

def save_profile(username, info):
    os.makedirs("profiles", exist_ok=True)
    json.dump(info, open(f"profiles/{username}.json", "w"), indent=4)

def load_profile(username):
    try: return json.load(open(f"profiles/{username}.json", "r"))
    except: return {}

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def listen_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening...")
        audio = r.listen(source)
    try:
        return r.recognize_google(audio)
    except:
        return "Sorry, couldn't understand."

# ---------- Session State Initialization ----------
for k in ["logged_in", "username", "profile_updated", "show_home", "soil_data", "chat"]:
    if k not in st.session_state:
        st.session_state[k] = False if k in ["logged_in", "profile_updated", "show_home"] else "" if k == "username" else []

# ---------- Authentication ----------
users = load_users()
if not st.session_state.logged_in and not st.session_state.show_home:
    st.title("🧑‍🌾 Farmer Assistant Login")
    auth_mode = st.radio("Select:", ["Sign In", "Sign Up"], horizontal=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if auth_mode == "Sign Up":
        confirm = st.text_input("Confirm Password", type="password")
        if st.button("Register"):
            if username in users:
                st.error("Username exists.")
            elif password != confirm:
                st.error("Passwords don't match.")
            elif not username or not password:
                st.warning("Fill all fields.")
            else:
                users[username] = hash_password(password)
                save_users(users)
                st.success("✅ Account created.")
    else:
        if st.button("Login"):
            if username in users and users[username] == hash_password(password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome, {username}!")
            else:
                st.error("Invalid login.")

# ---------- Profile Setup ----------
if st.session_state.logged_in and not st.session_state.show_home:
    st.header("👤 Profile Setup")
    profile = load_profile(st.session_state.username)
    name = st.text_input("Full Name", value=profile.get("name", ""))
    email = st.text_input("Email", value=profile.get("email", ""))
    location = st.text_input("Location", value=profile.get("location", ""))
    pic = st.file_uploader("Upload Profile Picture", type=["jpg", "jpeg", "png"])
    if st.button("Save Profile"):
        save_profile(st.session_state.username, {"name": name, "email": email, "location": location})
        if pic:
            os.makedirs("profile_pics", exist_ok=True)
            with open(f"profile_pics/{st.session_state.username}.jpg", "wb") as f:
                f.write(pic.read())
        st.session_state.show_home = True
        st.rerun()

# ---------- Main App ----------
if st.session_state.show_home:
    st.sidebar.success(f"Logged in as: {st.session_state.username}")
    menu = st.sidebar.selectbox("Navigate", ["🏠 Dashboard", "🧪 Soil Data", "💬 Chatbot", "🚪 Logout"])

    # --- Crop Model Training ---
    def train_crop_model():
        df = pd.DataFrame({
            "N": [90, 40, 60, 80], "P": [40, 35, 50, 60], "K": [40, 60, 70, 80],
            "temperature": [21, 23, 25, 28], "humidity": [80, 65, 75, 60],
            "ph": [6.5, 7.0, 6.2, 6.8], "rainfall": [200, 150, 180, 210],
            "label": ["tomato", "chili", "tomato", "onion"]
        })
        X, y = df.drop("label", axis=1), df["label"]
        model = RandomForestClassifier().fit(X, y)
        os.makedirs("models", exist_ok=True)
        joblib.dump(model, "models/crop_model.pkl")
        return model

    model = joblib.load("models/crop_model.pkl") if os.path.exists("models/crop_model.pkl") else train_crop_model()

    class Assistant:
        def get_variety(self): return ["PKM-1", "Arka Vikas"]
        def get_weather(self): return [{"day": d, "forecast": f} for d, f in zip(["Mon","Tue","Wed"], ["☀️", "🌧️", "⛅"])]
        def get_prices(self): return {"Tomato": {"Salem": "₹30/kg", "Madurai": "₹28/kg"}}
        def get_tip(self): return "Use organic compost before planting."

    bot = Assistant()

    # --- Dashboard ---
    if menu == "🏠 Dashboard":
        st.title("🌿 Farmer Assistant Dashboard")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🌱 Recommended Varieties")
            if st.button("Show Varieties"):
                st.success(", ".join(bot.get_variety()))

            st.subheader("🌦️ Weather")
            if st.button("Show Forecast"):
                for f in bot.get_weather():
                    st.write(f"**{f['day']}**: {f['forecast']}")

        with col2:
            st.subheader("📊 Market Prices")
            if st.button("Show Prices"):
                for crop, cities in bot.get_prices().items():
                    st.write(f"**{crop}**:")
                    for city, price in cities.items():
                        st.info(f"{city}: {price}")

        st.subheader("🎤 Voice Assistant")
        if st.button("🎤 Listen"):
            query = listen_command()
            st.write("You said:", query)
            tip = bot.get_tip()
            st.success("Assistant: " + tip)
            speak(tip)

        st.subheader("🌾 Field Activity Ideas")
        if st.button("💡 Show Field Ideas"):
            ideas = [
                "- 🌱 Mulching to conserve soil moisture",
                "- 🧪 Soil testing before planting",
                "- 🐛 Neem oil for pest control",
                "- 💧 Drip irrigation",
                "- 🌾 Crop rotation",
                "- 🚜 Deep plowing",
                "- 📦 Post-harvest storage",
                "- 🔁 Intercropping",
                "- ☀️ Solar fencing"
            ]
            for idea in ideas:
                st.markdown(idea)

    # --- Soil Data ---
    elif menu == "🧪 Soil Data":
        st.header("🧪 Enter Soil Conditions")
        ph = st.number_input("Soil pH", 0.0, 14.0)
        moisture = st.slider("Moisture (%)", 0, 100)
        nitrogen = st.number_input("Nitrogen (mg/kg)")
        phosphorus = st.number_input("Phosphorus (mg/kg)")
        potassium = st.number_input("Potassium (mg/kg)")
        notes = st.text_area("Notes (optional)")
        if st.button("Save Entry"):
            st.session_state.soil_data.append({
                "User": st.session_state.username,
                "pH": ph, "Moisture": moisture, "Nitrogen": nitrogen,
                "Phosphorus": phosphorus, "Potassium": potassium,
                "Notes": notes
            })
            st.success("Soil data saved.")

        st.header("📁 My Records")
        df = pd.DataFrame([r for r in st.session_state.soil_data if r["User"] == st.session_state.username])
        st.dataframe(df) if not df.empty else st.info("No records found.")

    # --- Chatbot ---
    elif menu == "💬 Chatbot":
        st.header("💬 AI Chat (Gemini)")
        if not st.session_state.chat:
            st.session_state.chat.append({"role": "system", "content": "You are a helpful agriculture assistant."})

        for msg in st.session_state.chat[1:]:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])

        prompt = st.chat_input("Ask something...")
        if prompt:
            st.chat_message("user").markdown(prompt)
            st.session_state.chat.append({"role": "user", "content": prompt})
            with st.chat_message("assistant"):
                try:
                    conversation = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.chat])
                    response = model.generate_content(conversation)
                    reply = response.text
                except Exception as e:
                    reply = f"Error: {e}"
                st.markdown(reply)
                st.session_state.chat.append({"role": "assistant", "content": reply})

    # --- Logout ---
    elif menu == "🚪 Logout":
        for k in list(st.session_state.keys()):
            st.session_state[k] = [] if k in ["soil_data", "chat"] else False if k not in ["username"] else ""
        st.rerun()
