import streamlit as st
import requests
import pandas as pd
import io
import random

# Set page configuration
st.set_page_config(page_title="Meal Plan Generator", page_icon="🍽️", layout="wide")

# CSS Styling: Sidebar Color, Recipe Card Styling with Border and Hover effect
st.markdown(
    """
    <style>
        .stApp {
            background-color: white;
        }
        /* Sidebar color */
        section[data-testid="stSidebar"] > div:first-child {
            background-color: #93B6F2;
        }
        /* Style the buttons to be blue */
        .stButton > button {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            margin-top: 10px;
        }
        /* Style the recipe cards with a border, shadow, and padding */
        .recipe-container {
            border: 1px solid #d4d4d4;
            padding: 20px;
            border-radius: 8px;
            background-color: white;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            margin-bottom: 20px;
            width: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .recipe-container:hover {
            border-color: #007bff;
        }
        .recipe-container img {
            border-radius: 8px;
            width: 100%;
            height: 200px;
            object-fit: cover;
            margin-bottom: 10px;
        }
        .recipe-container button {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            margin-top: 10px;
        }
        .recipe-container a {
            color: #007bff;
        }
        .recipe-container select, .recipe-container button {
            margin-top: 10px;
        }
        .recipe-container .recipe-actions {
            margin-top: 15px;
            padding-top: 10px;
            width: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# API credentials from Streamlit Secrets (stored in Streamlit Cloud)
EDAMAM_APP_ID = st.secrets["app_id"]
EDAMAM_APP_KEY = st.secrets["app_key"]

# Days of the week
days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Initialize the meal plan to persist data using session state
if "meal_plan" not in st.session_state:
    st.session_state.meal_plan = {day: [] for day in days_of_week}

# Fetch API data without caching
def fetch_recipes(query, diet_type, calorie_limit):
    # API endpoint for Edamam Recipes API
    BASE_URL = "https://api.edamam.com/api/recipes/v2"
    
    # Build the query parameters for the API request
    params = {
        "type": "public",
        "q": query,
        "app_id": EDAMAM_APP_ID,
        "app_key": EDAMAM_APP_KEY,
    }
    
    # Add optional filters
    if diet_type != "None":
        params["diet"] = diet_type.lower()
    if calorie_limit > 0:
        params["calories"] = f"lte {calorie_limit}"
    
    # Send API request
    response = requests.get(BASE_URL, params=params)
    
    if response.status_code == 200:
        results = response.json().get("hits", [])
        # Shuffle the results to get a different set of recipes each time
        random.shuffle(results)
        return results
    else:
        st.error(f"API request failed with status code {response.status_code}")
        st.write(response.text)
        return []

# Sidebar options for search filters and search query (Search input first)
st.sidebar.title("Meal Plan Options")
query = st.sidebar.text_input("Search for recipes (e.g., chicken, vegan pasta)", "dinner")
diet_type = st.sidebar.selectbox("Select Diet", ["Balanced", "Low-Carb", "High-Protein", "None"], index=0)
calorie_limit = st.sidebar.number_input("Max Calories (Optional)", min_value=0, step=50)
if st.sidebar.button("Search Recipes"):
    st.session_state.recipes = fetch_recipes(query, diet_type, calorie_limit)

# Track selected day for each recipe in session state
if "selected_days" not in st.session_state:
    st.session_state.selected_days = {}

# Helper function to add recipes to the meal plan
def add_recipe_to_day(day, recipe):
    st.session_state.meal_plan[day].append(recipe)

# Show recipes if search has been performed
if "recipes" in st.session_state:
    recipes = st.session_state.recipes
    if recipes:
        st.write(f"## Showing {len(recipes)} recipes for **{query}**")
        cols = st.columns(5)  # 5 columns in a row
        for idx, recipe_data in enumerate(recipes):
            recipe = recipe_data["recipe"]
            recipe_key = f"recipe_{idx}"
            if recipe_key not in st.session_state.selected_days:
                st.session_state.selected_days[recipe_key] = "Monday"  # Default to Monday if not chosen

            with cols[idx % 5]:  # Switch to 5 columns
                st.markdown(f"""
                <div class="recipe-container">
                    <img src="{recipe['image']}" alt="Recipe Image"/>
                    <h4>{recipe['label']}</h4>
                    <p>Calories: {recipe['calories']:.0f}</p>
                    <a href="{recipe['url']}" target="_blank">View Recipe</a>
                    <div class="recipe-actions">
                        <label>Choose day for {recipe['label']}:</label>
                """, unsafe_allow_html=True)

                selected_day = st.selectbox(
                    f"Choose day for {recipe['label']}",
                    days_of_week,  # Days of the week
                    key=f"day_{recipe_key}"
                )
                if st.button(f"Add {recipe['label']} to {selected_day}", key=f"btn_{idx}"):
                    add_recipe_to_day(selected_day, recipe)

                st.markdown("</div></div>", unsafe_allow_html=True)

# Display the meal plan in a calendar-like format
st.write("## Your Meal Plan")
cols = st.columns(7)
for idx, (day, meals) in enumerate(st.session_state.meal_plan.items()):
    with cols[idx % 7]:
        st.write(f"### {day}")
        if meals:
            for meal in meals:
                st.write(f"- [{meal['label']}]({meal['url']}) ({meal['calories']:.0f} calories)")
        else:
            st.write("No meals added yet.")

# Input for number of people before generating the shopping list
people = st.sidebar.number_input("How many people?", min_value=1, value=1)

# Generate shopping list button
if st.sidebar.button("Generate Shopping List"):
    shopping_list = {}
    for meals in st.session_state.meal_plan.values():
        for recipe in meals:
            for ingredient in recipe["ingredients"]:
                food_item = ingredient["food"]
                quantity = ingredient["quantity"] * people  # Adjusting for number of people
                unit = ingredient.get("measure", "units")  # Adding units like grams, kilograms, etc.
                if food_item in shopping_list:
                    shopping_list[food_item]["quantity"] += quantity
                else:
                    shopping_list[food_item] = {"quantity": quantity, "unit": unit}

    # Display the shopping list
    st.write("## Shopping List")
    for food, details in shopping_list.items():
        st.write(f"{food}: {details['quantity']} {details['unit']}")

# Function to download meal plans as CSV (fixed to output valid text format)
def download_meal_plan():
    output = io.StringIO()  # Use in-memory string buffer for CSV format
    output.write("Day,Recipe,URL\n")  # Correct header for CSV
    
    # Iterate through the meal plan and write to CSV
    for day, meals in st.session_state.meal_plan.items():
        for meal in meals:
            output.write(f"{day},{meal['label']},{meal['url']}\n")
    
    # Ensure the buffer is ready for download
    output.seek(0)
    return output

# Button to download meal plan as a CSV file
if st.button("Download Meal Plan as CSV"):
    csv_data = download_meal_plan()
    st.download_button(
        label="Download CSV File",
        data=csv_data.getvalue(),  # Getting the string value from StringIO
        file_name="meal_plan.csv",
        mime="text/csv"
    )

