from flask import Flask, render_template, request
import os
import google.generativeai as genai
from dotenv import load_dotenv
from waitress import serve  # For stable production deployment

# Load environment variables
load_dotenv()

# Set up Google Gemini API Key
google_api_key = os.getenv('GOOGLE_API_KEY')
if not google_api_key:
    raise ValueError("Missing Google API Key. Set GOOGLE_API_KEY environment variable.")

genai.configure(api_key=google_api_key)

def get_gemini_response(prompt):
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    response = model.generate_content(prompt)
    return response.text.replace("\n", "<br>")  # Formatting for HTML display

# BMI Calculation
def calculate_bmi(weight, height):
    height_m = height / 100  # Convert cm to meters
    return round(weight / (height_m ** 2), 2)

# BMR Calculation
def calculate_bmr(weight, height, age, gender):
    if gender.lower() == "male":
        return round(88.36 + (13.4 * weight) + (4.8 * height) - (5.7 * age), 2)
    else:
        return round(447.6 + (9.2 * weight) + (3.1 * height) - (4.3 * age), 2)

# Protein Requirement Calculation
def calculate_protein(weight):
    return round(weight * 1.2, 2)  # 1.2g protein per kg body weight

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    # Get user input
    age = int(request.form['age'])
    gender = request.form['gender']
    weight = float(request.form['weight'])
    height = float(request.form['height'])
    workout_goal = request.form['workout_goal']
    custom_goal = request.form.get('custom_goal', '').strip()
    diet_type = request.form['diet_type']  # Vegetarian, Non-Vegetarian, Vegan

    # If 'Other' is chosen in workout_goal, use custom goal input
    selected_goal = custom_goal if workout_goal == "Other" and custom_goal else workout_goal

    # Calculate health metrics
    bmi = calculate_bmi(weight, height)
    bmr = calculate_bmr(weight, height, age, gender)
    protein_requirement = calculate_protein(weight)

    # Create prompt for workout plan
    workout_prompt = f"""
    Create a detailed gym and yoga workout plan for Monday to Saturday based on the user's goal: {selected_goal}.
    - Each day should focus on a specific muscle group.
    - Include 4-5 gym exercises and one yoga pose per day.
    - The plan should be structured cleanly.
    """

    # Create prompt for meal plan
    meal_prompt = f"""
    Provide a **7-day meal plan** (Monday to Sunday) with Breakfast, Lunch, and Dinner based on a **{diet_type}** diet and workout goal: {selected_goal}.
    - Meals should be simple and nutritious.
    - Only include food items that fit the selected diet type.
    - Just list the meals for each day.
    """

    # Fetch AI responses
    workout_plan = get_gemini_response(workout_prompt)
    meal_plan = get_gemini_response(meal_prompt)

    return render_template('result.html', bmi=bmi, bmr=bmr, protein=protein_requirement, 
                           workout_plan=workout_plan, meal_plan=meal_plan)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)







