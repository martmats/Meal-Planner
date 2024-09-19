import streamlit as st
import requests
import pandas as pd
# Set page configuration
st.set_page_config(page_title="Menu Planner", page_icon="🍽️", layout="wide")
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

# Initialize the meal plan in session state if it's not already there
# Initialize the meal plan to persist data using session state
if "meal_plan" not in st.session_state:
    st.session_state.meal_plan = {f"Day {i+1}": [] for i in range(7)}
    st.session_state.meal_plan = {day: [] for day in days_of_week}

# Initialize selected days in session state if not already present
# Initialize the selected_days in session state
if "selected_days" not in st.session_state:
    st.session_state.selected_days = {}

        st.write(response.text)
        return []

# Sidebar options for search filters and search query
st.sidebar.title("Meal Plan Options")
diet_type = st.sidebar.selectbox("Select Diet", ["Balanced", "Low-Carb", "High-Protein", "None"], index=0)
calorie_limit = st.sidebar.number_input("Max Calories (Optional)", min_value=0, step=50)
query = st.sidebar.text_input("Search for recipes (e.g., chicken, vegan pasta)", "dinner")
# Clear previous results if the search button is clicked
if st.sidebar.button("Search Recipes"):
    clear_recipe_cache()
if "recipes" in st.session_state:
    recipes = st.session_state.recipes
    if recipes:
        st.markdown('<div id="meal-plan"></div>', unsafe_allow_html=True)
        st.write(f"## Showing {len(recipes)} recipes for **{query}**")
        cols = st.columns(5)  # 5 columns in a row
        for idx, recipe_data in enumerate(recipes):
                    add_recipe_to_day(selected_day, recipe)

# Display the meal plan in a calendar-like format with recipe URL
st.markdown('<div id="shopping-list"></div>', unsafe_allow_html=True)
st.write("## Your Meal Plan")
cols = st.columns(7)
for idx, (day, meals) in enumerate(st.session_state.meal_plan.items()):
                    shopping_list[food_item] = {"quantity": quantity, "unit": unit}

    # Display the shopping list
    st.markdown('<div class="shopping-list"></div>', unsafe_allow_html=True)
    st.write("## Shopping List")
    for food, details in shopping_list.items():
        st.write(f"{food}: {details['quantity']} {details['unit']}")
        file_name="meal_plan.csv",
        mime="text/csv"
    )
