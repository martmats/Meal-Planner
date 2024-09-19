import streamlit as st
import requests
import pandas as pd
import io

# Set page configuration
st.set_page_config(page_title="Menu Planner", page_icon="🍽️", layout="wide")
st.set_page_config(page_title="Meal Plan Generator", page_icon="🍽️", layout="wide")

# Custom CSS for styling
# CSS Styling: Sidebar Color, Recipe Card Styling with Border and Hover effect
st.markdown(
    """
    <style>
        /* Sidebar styling */
        .stApp {
            background-color: white;
        }
        /* Sidebar color */
        section[data-testid="stSidebar"] > div:first-child {
            background-color: #93B6F2;
            padding: 20px;
            border-radius: 10px;
        }
        /* Sidebar title and icon */
        .sidebar-title {
            font-size: 26px;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .sidebar-title img {
            width: 30px;
            height: 30px;
        }
        /* Search box */
        .stTextInput > div > input {
            border: 2px solid #007bff;
            border-radius: 10px;
            padding: 8px;
            font-size: 16px;
        }
        /* Recipe button styling */
        .stButton button {
        /* Style the buttons to be blue */
        .stButton > button {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 10px;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            margin-top: 10px;
        }
        /* Recipe cards styling */
        /* Style the recipe cards with a border, shadow, and padding */
        .recipe-container {
            border: 2px solid #d4d4d4;
            border: 1px solid #d4d4d4;
            padding: 20px;
            border-radius: 10px;
            border-radius: 8px;
            background-color: white;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 40px;  /* Increased spacing between cards */
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
            border-radius: 10px;
            border-radius: 8px;
            width: 100%;
            height: 200px;
            object-fit: cover;
        }
        .recipe-container h4 {
            font-size: 20px;
            font-weight: bold;
            margin-top: 15px;
        }
        .recipe-container p {
            font-size: 16px;
            margin-bottom: 15px;
        }
        .recipe-container button {
            background-color: #28a745;
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 10px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
        }
        /* Increase spacing between layout columns */
        [data-testid="column"] {
            gap: 20px;
        }
        /* Fix spacing for section buttons */
        .menu-buttons {
            margin-top: 20px;
            display: flex;
            gap: 20px;
        }
        /* Shopping list styling */
        .shopping-list {
            margin-top: 20px;
        }
        .shopping-list h2 {
            font-size: 22px;
            font-weight: bold;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar title and search input at the top
st.sidebar.markdown(
    """
    <div class="sidebar-title">
        <img src="https://www.flaticon.com/svg/static/icons/svg/2921/2921822.svg" alt="icon"/>
        Menu Planner
    </div>
    """,
    unsafe_allow_html=True,
)
# Days of the week for meal plan
days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Search box input (moved to the top of the sidebar)
query = st.sidebar.text_input("Search for recipes (e.g., chicken, vegan pasta)", "dinner")
# Initialize the meal plan to persist data using session state
if "meal_plan" not in st.session_state:
    st.session_state.meal_plan = {day: [] for day in days_of_week}

# Add buttons for navigation
st.sidebar.markdown(
    """
    <div class="menu-buttons">
        <button onclick="window.location.href='#meal-plan'">Go to Menu Planner</button>
        <button onclick="window.location.href='#shopping-list'">Go to Shopping List</button>
    </div>
    """,
    unsafe_allow_html=True,
)
# Initialize the selected_days in session state
if "selected_days" not in st.session_state:
    st.session_state.selected_days = {}

# Function to clear cached results
def clear_recipe_cache():
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
