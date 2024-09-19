import streamlit as st
import requests
import pandas as pd
import io
import random
import time  # For randomization

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
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Days of the week for meal plan
days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Initialize the meal plan to persist data using session state
if "meal_plan" not in st.session_state:
    st.session_state.meal_plan = {day: [] for day in days_of_week}

# Initialize the selected_days in session state
if "selected_days" not in st.session_state:
    st.session_state.selected_days = {}

# Function to clear cached results
def clear_recipe_cache():
    if "recipes" in st.session_state:
        del st.session_state["recipes"]
    if "next_page_url" in st.session_state:
        del st.session_state["next_page_url"]

# Function to fetch recipes with randomization in the query (adds unused random parameter)
def fetch_recipes(query, diet_type, calorie_limit, next_page=None):
    if next_page:
        url = next_page  # Use next page URL for pagination
    else:
        url = "https://api.edamam.com/api/recipes/v2"
        # Add a random timestamp to make each query unique
        random_seed = random.randint(1, 10000)
        params = {
            "type": "public",
            "q": query,  # Keep the search query unchanged
            "app_id": st.secrets["app_id"],  # Your App ID
            "app_key": st.secrets["app_key"],  # Your App Key
            "random": random_seed,  # Unused parameter to randomize the request
            "diet": diet_type,
            "calories": calorie_limit,
        }
        # Fetch the data
        response = requests.get(url, params=params)
        data = response.json()
        return data

# Fetch new results when the app starts
if "recipes" not in st.session_state:
    st.session_state.recipes = fetch_recipes("popular", None, None)
    st.experimental_rerun()  # Trigger a rerun to load new results on startup

# Search function triggered by user
def search_recipes():
    query = st.text_input("Search for recipes", "")
    diet_type = st.selectbox("Choose a diet type", ["None", "Balanced", "Low-Carb", "High-Protein"])
    calorie_limit = st.slider("Set calorie limit", 100, 2000, 500)

    if st.button("Search"):
        st.session_state.recipes = fetch_recipes(query, diet_type, calorie_limit)
        st.experimental_rerun()

# Display the recipes
def display_recipes(recipes):
    for recipe in recipes.get("hits", []):
        st.markdown(
            f"""
            <div class="recipe-container">
                <img src="{recipe['recipe']['image']}" alt="{recipe['recipe']['label']}">
                <h3>{recipe['recipe']['label']}</h3>
                <p>Calories: {recipe['recipe']['calories']:.2f}</p>
                <a href="{recipe['recipe']['url']}" target="_blank">View Recipe</a>
            </div>
            """,
            unsafe_allow_html=True,
        )

# Display meal plan and shopping list
def display_meal_plan():
    st.header("Your Meal Plan")
    for day in days_of_week:
        st.subheader(day)
        for recipe in st.session_state.meal_plan[day]:
            st.markdown(f"- {recipe['label']}")

    if st.button("Generate Shopping List"):
        generate_shopping_list()

# Generate shopping list based on meal plan
def generate_shopping_list():
    shopping_list = {}
    for day, recipes in st.session_state.meal_plan.items():
        for recipe in recipes:
            for ingredient in recipe['ingredients']:
                shopping_list[ingredient] = shopping_list.get(ingredient, 0) + 1

    shopping_list_str = "\n".join([f"{item}: {count}" for item, count in shopping_list.items()])
    st.text_area("Shopping List", shopping_list_str)

    # Allow user to download the shopping list as a CSV
    if st.button("Download Shopping List as CSV"):
        download_csv(shopping_list)

# Download the meal plan as a CSV
def download_csv(shopping_list):
    df = pd.DataFrame(list(shopping_list.items()), columns=["Ingredient", "Quantity"])
    csv = df.to_csv(index=False)
    st.download_button(label="Download CSV", data=csv, file_name="shopping_list.csv", mime="text/csv")

# Main app execution
st.title("Meal Planner and Recipe Finder")
search_recipes()
if "recipes" in st.session_state:
    display_recipes(st.session_state.recipes)
display_meal_plan()
