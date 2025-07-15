# farmer_assistant_combined.py
# Auto-generated combined script


import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import playsound
import os
import json
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout


# --- Voice I/O ---

import speech_recognition as sr
from gtts import gTTS
import playsound
import os

def listen_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
        try:
            return r.recognize_google(audio)
        except:
            return "Could not understand."

def speak(text):
    tts = gTTS(text=text, lang='en')
    filename = "temp_voice.mp3"
    tts.save(filename)
    playsound.playsound(filename)
    os.remove(filename)

# --- Utility Functions ---

import json
import os

# --- Load local JSON file ---
def load_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return {}

# --- Load plain text file ---
def load_text(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return "No data available."

# --- Example: Load preloaded weather forecast ---
def get_static_weather(location="Kodaikanal"):
    data = load_json("data/weather.json")
    return data.get(location, [])

# --- Example: Get local market prices ---
def get_market_prices(crop="Tomato"):
    data = load_json("data/tomato_prices.json")
    return data.get(crop, {})

# --- Example: Get scheme info from text ---
def get_government_schemes():
    return load_text("data/schemes.txt")


# --- Assistant Logic ---

def get_crop_variety(soil, season):
    if soil == "Red Loamy Soil" and season == "Kharif":
        return ["Arka Rakshak", "PKM-1", "Sankranti"]
    return ["Default Variety"]

def get_weather_forecast(location):
    return [
        {"day": "Monday", "forecast": "Cloudy"},
        {"day": "Tuesday", "forecast": "Rain expected"},
        # Load from data/weather.json in full version
    ]

def get_fertilizer_tips(stage):
    if stage == "Pre-Planting":
        return "Apply 10 tons of compost per acre. Avoid excess nitrogen before transplanting."

def get_disease_warnings(region="Tamil Nadu"):
    return "Watch out for early blight and leaf curl virus in tomato crops."

def get_market_prices():
    return {"Dindigul": "₹28/kg", "Madurai": "₹26/kg"}

def get_government_schemes():
    return "You may be eligible for PM-KISAN ₹6,000/year support. Contact your local Agri Office."

def get_climate_suggestions():
    return "Use mulching and drip irrigation to conserve water. Choose drought-tolerant seeds."

# --- Leaf Disease Model Training ---

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
import numpy as np
import os

# Dummy data: 100 images of size 224x224x3, 3 classes
X = np.random.rand(100, 224, 224, 3)
y = np.random.randint(0, 3, 100)

# Build the CNN model
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
    MaxPooling2D(2, 2),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D(2, 2),
    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.3),
    Dense(3, activation='softmax')
])

# Compile and train
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
model.fit(X, y, epochs=3, batch_size=8, verbose=1)

# Save model
os.makedirs("models", exist_ok=True)
model.save("models/leaf_disease_model.h5")

# Save label names
with open("models/labels.txt", "w") as f:
    f.write("Tomato - Healthy\nTomato - Early Blight\nTomato - Leaf Curl Virus")

print("✅ Model and labels saved in models/")


# --- Crop Model Training ---

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

# Sample dataset (minimal example)
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

# Features and label
X = df.drop("label", axis=1)
y = df["label"]

# Split (optional for real training)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train the model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Save model to file
joblib.dump(model, "models/crop_model.pkl")

print("✅ crop_model.pkl created successfully.")


# --- Embedded Text and JSON Data ---

schemes_text = """🌾 GOVERNMENT SCHEMES FOR TOMATO FARMERS

1. PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)
   - ₹6,000 annual income support to small and marginal farmers.
   - Paid in three equal installments of ₹2,000.
   - Registration via local agriculture office or online at pmkisan.gov.in.

2. Rashtriya Krishi Vikas Yojana (RKVY)
   - Financial support for modern farming equipment and techniques.
   - Priority to horticulture crops like tomato.

3. Tamil Nadu State Horticulture Mission
   - Subsidy for drip irrigation, mulching, and greenhouse tomato cultivation.
   - Apply through TN horticulture department offices.

4. Kisan Credit Card (KCC)
   - Low-interest short-term credit for seeds, fertilizers, irrigation.
   - Apply via local banks with Aadhaar + land proof.

5. PMFBY (Pradhan Mantri Fasal Bima Yojana)
   - Crop insurance scheme to protect against crop failure.
   - Premium: 2% for Kharif crops like tomato.

6. National Horticulture Board (NHB) Subsidies
   - Support for post-harvest storage and marketing of perishable crops.
   - Suitable for tomato growers storing or selling in bulk.

📌 Visit your nearest agriculture office for help in applying.
📞 Toll-free helpline: 1800-180-1551"""

labels_text = """Tomato - Healthy
Tomato - Early Blight
Tomato - Leaf Curl Virus"""

weather_data = {
  "Kodaikanal": [
    {
      "day": "Monday",
      "forecast": "Cloudy with light rain"
    },
    {
      "day": "Tuesday",
      "forecast": "Moderate rainfall expected"
    },
    {
      "day": "Wednesday",
      "forecast": "Partly sunny with clouds"
    },
    {
      "day": "Thursday",
      "forecast": "Thunderstorms possible"
    },
    {
      "day": "Friday",
      "forecast": "Clear and dry"
    },
    {
      "day": "Saturday",
      "forecast": "Light fog in the morning"
    },
    {
      "day": "Sunday",
      "forecast": "Rain likely in the evening"
    }
  ],
  "Madurai": [
    {
      "day": "Monday",
      "forecast": "Sunny and dry"
    },
    {
      "day": "Tuesday",
      "forecast": "Hot with haze"
    },
    {
      "day": "Wednesday",
      "forecast": "Clear skies"
    },
    {
      "day": "Thursday",
      "forecast": "Warm and humid"
    },
    {
      "day": "Friday",
      "forecast": "Dry with slight breeze"
    },
    {
      "day": "Saturday",
      "forecast": "Partly cloudy"
    },
    {
      "day": "Sunday",
      "forecast": "Possible rain late night"
    }
  ]
}

tomato_prices_data = {
  "Tomato": {
    "Dindigul": "\u20b928/kg",
    "Madurai": "\u20b926/kg",
    "Salem": "\u20b930/kg",
    "Coimbatore": "\u20b927/kg",
    "Trichy": "\u20b929/kg"
  }
}
