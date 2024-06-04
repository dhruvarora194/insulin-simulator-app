import streamlit as st
import openai
from PIL import Image
from pydexcom import Dexcom
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
from config import OPENAI_API_KEY, DEXCOM_USERNAME, DEXCOM_PASSWORD
import re
import docx2txt

# Set up OpenAI API
openai.api_key = OPENAI_API_KEY

# Initialize Dexcom
dexcom = Dexcom(DEXCOM_USERNAME, DEXCOM_PASSWORD)

# Function to fetch glucose data from Dexcom
def fetch_glucose_data(dexcom, minutes):
    try:
        glucose_data = dexcom.get_glucose_readings(minutes=minutes)
        return [reading.value for reading in glucose_data]
    except Exception as e:
        st.write(f"Error fetching glucose data: {e}")
        return None

# Function to get the latest blood sugar reading from Dexcom
def get_latest_blood_sugar(dexcom):
    try:
        glucose_data = dexcom.get_glucose_readings(minutes=5)
        if glucose_data:
            return glucose_data[-1].value
        else:
            return None
    except Exception as e:
        st.write(f"Error fetching latest blood sugar: {e}")
        return None

# Function to extract nutritional information using OpenAI
def get_nutritional_info(food_description):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are an expert nutritionist. Provide detailed nutritional information in the following format: 'Carbohydrates: X grams, Protein: Y grams, Fat: Z grams, Calories: W kcal, Sodium: V mg, Sugar: U grams, Fiber: T grams'."
            },
            {
                "role": "user",
                "content": f"Extract the nutritional information from this description: {food_description}"
            }
        ]
    )
    return response['choices'][0]['message']['content'].strip()

# Function to calculate insulin dose
def calculate_insulin_dose(carbs, ic_ratio, activity_factor, current_blood_sugar, target_blood_sugar, correction_factor):
    insulin_for_carbs = (carbs / ic_ratio) * activity_factor
    correction_dose = (current_blood_sugar - target_blood_sugar) / correction_factor
    return insulin_for_carbs + correction_dose

# Function to suggest tips to avoid blood sugar spikes
def suggest_tips(food_description):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are an expert nutritionist."
            },
            {
                "role": "user",
                "content": f"Provide suggestions on how to avoid blood sugar spikes when eating this meal: {food_description}. Include tips like eating greens with high carbs."
            }
        ]
    )
    return response['choices'][0]['message']['content'].strip()

# Time to inject based on insulin type
def time_to_inject(insulin_type):
    times = {
        'Novolog': 15,
        'Fiasp': 10,
        'Humalog': 15,
        'Regular': 30
    }
    return times.get(insulin_type, 15)  # Default to 15 minutes if insulin type is unknown

# Load and display a background image
background_image_path = "background.jpg"  # Path to your local background image
background_image = Image.open(background_image_path)
st.image(background_image, use_column_width=True)

# Streamlit app
st.title("Insulin Simulator App for Type 1 Diabetes")

# Fetch Dexcom data
st.write("### Blood Sugar Levels (Past 2 Hours)")
glucose_values = fetch_glucose_data(dexcom, 120)  # 120 minutes = 2 hours
if glucose_values:
    current_time = datetime.now()
    time_labels = [(current_time - timedelta(minutes=i * 5)).strftime('%I:%M %p') for i in range(len(glucose_values))]
    
    plt.figure(figsize=(10, 5))
    plt.plot(time_labels[::-1], glucose_values[::-1], label="Blood Sugar")  # Reverse both time labels and glucose values to mirror trend line
    plt.xlabel("Time")
    plt.ylabel("Blood Sugar Level (mg/dL)")
    plt.ylim(70, 250)
    plt.xticks(rotation=45)
    plt.title("Blood Sugar Levels (Past 2 Hours)")
    plt.legend()
    st.pyplot(plt)
else:
    st.write("Failed to fetch glucose data from Dexcom.")

# User Inputs
st.write("### User Inputs")

insulin_type = st.selectbox("Select your type of insulin", ["Novolog", "Fiasp", "Humalog", "Regular"])
ic_ratio = st.slider("Enter your Insulin to Carb Ratio (I:C)", min_value=1, max_value=20, value=10, step=1)
correction_factor = st.slider("Enter your Correction Factor", min_value=10, max_value=100, value=50, step=1)
activity_level = st.selectbox("Select your activity level", ["Low", "Moderate", "High"])
target_blood_sugar = st.number_input("Enter your target blood sugar level (mg/dL)", min_value=70, max_value=150, value=100)

# User Inputs for food item
food_item = st.text_input("Enter the name of the food item")

# Field to upload recipe as text or word file
st.write("### Upload Recipe")
recipe_file = st.file_uploader("Upload a recipe as a text or word file", type=["txt", "docx"])

if recipe_file is not None:
    if recipe_file.type == "text/plain":
        recipe_text = str(recipe_file.read(), "utf-8")
    elif recipe_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        recipe_text = docx2txt.process(recipe_file)

    st.write("Extracted Recipe Text:")
    st.write(recipe_text)

def display_insulin_dose(food_description, ic_ratio, correction_factor, activity_level, current_blood_sugar, target_blood_sugar):
    nutritional_info = get_nutritional_info(food_description)

    # Extract macros from nutritional info
    carbs_match = re.search(r"Carbohydrates\s*:\s*(\d+)", nutritional_info, re.IGNORECASE)
    protein_match = re.search(r"Protein\s*:\s*(\d+)", nutritional_info, re.IGNORECASE)
    fat_match = re.search(r"Fat\s*:\s*(\d+)", nutritional_info, re.IGNORECASE)
    calories_match = re.search(r"Calories\s*:\s*(\d+)", nutritional_info, re.IGNORECASE)
    sodium_match = re.search(r"Sodium\s*:\s*(\d+)", nutritional_info, re.IGNORECASE)
    sugar_match = re.search(r"Sugar\s*:\s*(\d+)", nutritional_info, re.IGNORECASE)
    fiber_match = re.search(r"Fiber\s*:\s*(\d+)", nutritional_info, re.IGNORECASE)

    if carbs_match and protein_match and fat_match and calories_match and sodium_match and sugar_match and fiber_match:
        carbs = float(carbs_match.group(1))
        protein = float(protein_match.group(1))
        fat = float(fat_match.group(1))
        calories = float(calories_match.group(1))
        sodium = float(sodium_match.group(1))
        sugar = float(sugar_match.group(1))
        fiber = float(fiber_match.group(1))

        # Display nutritional information in a tabular format with vibrant colors
        nutritional_data = {
            "Nutrient": ["Carbohydrates", "Protein", "Fat", "Calories", "Sodium", "Sugar", "Fiber"],
            "Amount": [f"{carbs} grams", f"{protein} grams", f"{fat} grams", f"{calories} kcal", f"{sodium} mg", f"{sugar} grams", f"{fiber} grams"]
        }
        df_nutritional_info = pd.DataFrame(nutritional_data)
        st.write("### Nutritional Information")
        st.table(df_nutritional_info.style.set_properties(**{'background-color': 'lightblue', 'color': 'black'}))

        activity_factors = {
            'Low': 1.2,
            'Moderate': 1.0,
            'High': 0.8
        }
        activity_factor = activity_factors[activity_level]

        insulin_dose = calculate_insulin_dose(carbs, ic_ratio, activity_factor, current_blood_sugar, target_blood_sugar, correction_factor)
        st.write(f"Suggested Insulin Dose: {insulin_dose:.1f} units")

        injection_time = time_to_inject(insulin_type)
        st.write(f"Inject {injection_time} minutes before your meal.")

        tips = suggest_tips(food_description)
        st.write("### Tips to Avoid Blood Sugar Spikes")
        st.write(tips)

        if current_blood_sugar > 250:
            st.write("### ADDITIONAL TIPS: VERY HIGH BLOOD SUGAR")
            st.write("Your blood sugar levels are very high. Consider consulting your healthcare provider immediately.")
        elif current_blood_sugar > 200:
            st.write("### ADDITIONAL TIPS: HIGH BLOOD SUGAR")
            st.write("Your blood sugar levels are high. Consider reducing your carb intake, increasing your physical activity, or consulting your healthcare provider.")
        elif current_blood_sugar > 140:
            st.write("### ADDITIONAL TIPS: SLIGHTLY HIGH BLOOD SUGAR")
            st.write("Your blood sugar levels are slightly high. Consider moderate physical activity and balanced meals.")
        elif 90 <= current_blood_sugar <= 140:
            st.write("### ADDITIONAL TIPS: IN-RANGE BLOOD SUGAR")
            st.write("Your blood sugar levels are within range. Keep up the good work! Consider eating balanced meals with greens to maintain this level.")
        else:
            st.write("### ADDITIONAL TIPS: LOW BLOOD SUGAR")
            st.write("Your blood sugar levels are low. Consider consuming fast-acting carbohydrates like juice or glucose tablets and consulting your healthcare provider.")

# Submit button to process inputs
if st.button("Submit"):
    if food_item or recipe_file:
        if recipe_file:
            food_description = recipe_text
        else:
            food_description = food_item

        # Get the latest blood sugar reading from Dexcom
        current_blood_sugar = get_latest_blood_sugar(dexcom)
        if current_blood_sugar is None:
            st.write("Failed to fetch the latest blood sugar reading. Please try again later.")
        else:
            st.write(f"### CURRENT BLOOD SUGAR: {current_blood_sugar} MG/DL")
            display_insulin_dose(food_description, ic_ratio, correction_factor, activity_level, current_blood_sugar, target_blood_sugar)
    else:
        st.write("Please provide a food item or upload a recipe file.")
