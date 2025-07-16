import streamlit as st
import speech_recognition as sr
import pyttsx3
import requests
from PIL import Image
import openai
import json

# --- Streamlit Config ---
st.set_page_config(page_title="🌾 AI Farmer Assistant", layout="wide")

# --- API Key Setup (OpenRouter) ---
OPENROUTER_API_KEY = "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"  # ← Replace with your real key
openai.api_base = "https://openrouter.ai/api/v1"
openai.api_key = OPENROUTER_API_KEY

# --- TTS Setup ---
engine = pyttsx3.init()
def speak(text):
    engine.say(text)
    engine.runAndWait()

# --- Voice Recognition ---
def recognize_voice():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        st.info("🎤 Listening... Speak now.")
        audio = recognizer.listen(source, phrase_time_limit=5)
    try:
        text = recognizer.recognize_google(audio)
        st.success(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        st.error("Sorry, couldn't understand.")
    except sr.RequestError as e:
        st.error(f"Speech recognition error: {e}")
    return None

# --- AI Response (OpenRouter API) ---
def get_ai_response(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openai/gpt-4o",  # Change model if needed
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1000  # Prevent token limit error
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        st.error("AI error: " + response.text)
        return "AI bot failed to respond."

# --- Disease Detection Placeholder ---
def detect_disease(image):
    st.image(image, caption="Leaf Uploaded")
    return "Result: Leaf appears to be affected by Early Blight."

# --- Weather Advice Placeholder ---
def get_weather_advice():
    return "🌦️ Weather: Cloudy with chance of rain\n🌱 Suggested Crops: Paddy, Groundnut, Moong dal."

# --- Streamlit Tabs ---
st.title("🌾 AI Farmer Assistant")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🧠 AI Bot", "🎤 Voice Input", "🌿 Disease Detection", "🌦️ Weather Advice", "🔊 TTS"
])

with tab1:
    st.header("Talk to the AI")
    user_input = st.text_input("Ask something:")
    if st.button("Ask AI"):
        reply = get_ai_response(user_input)
        st.success(reply)
        speak(reply)

with tab2:
    st.header("Speak Your Question")
    if st.button("🎙️ Start Recording"):
        text = recognize_voice()
        if text:
            reply = get_ai_response(text)
            st.success(reply)
            speak(reply)

with tab3:
    st.header("Upload Leaf Image for Disease Detection")
    file = st.file_uploader("Upload image", type=["jpg", "jpeg", "png"])
    if file:
        img = Image.open(file)
        result = detect_disease(img)
        st.success(result)
        speak(result)

with tab4:
    st.header("Get Planting Advice")
    weather = get_weather_advice()
    st.text(weather)
    speak(weather)

with tab5:
    st.header("Text to Speech")
    tts_text = st.text_area("Enter text to read aloud")
    if st.button("Speak Text"):
        speak(tts_text)

