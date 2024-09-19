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
    </style>
    """,
    unsafe_allow_html=True
)

# Fetch recipes from API function
def get_recipes(query):
    url = f"https://api.edamam.com/search?q={query}&app_id=YOUR_APP_ID&app_key=YOUR_APP_KEY&from=0&to=100"
    response = requests.get(url)
    data = response.json()
    
    if 'hits' in data:
        recipes = data['hits']
        return [recipe['recipe'] for recipe in recipes]
    else:
        return []

# Function to display a random set of recipes
def display_random_recipes(recipes, num_to_display=5):
    random.shuffle(recipes)  # Shuffle the recipes to get random ones each time
    
    # Keep track of displayed recipes to avoid repeats
    if "displayed_recipes" not in st.session_state:
        st.session_state.displayed_recipes = []

    # Exclude previously displayed recipes
    new_recipes = [recipe for recipe in recipes if recipe['label'] not in st.session_state.displayed_recipes]

    # Select the recipes to display and update the session state to avoid repeats
    for recipe in new_recipes[:num_to_display]:
        st.markdown(f"""
            <div class="recipe-container">
                <img src="{recipe['image']}" alt="{recipe['label']}">
                <h3>{recipe['label']}</h3>
                <p>Calories: {recipe['calories']:.0f}</p>
                <a href="{recipe['url']}" target="_blank"><button>View Recipe</button></a>
            </div>
        """, unsafe_allow_html=True)
        
        # Add the recipe label to the session state to avoid showing it again
        st.session_state.displayed_recipes.append(recipe['label'])

# Sidebar input for search query
search_term = st.sidebar.text_input("Search for recipes (e.g., chicken, beef, vegan)", "")

# Buttons to navigate to sections
if st.sidebar.button("Go to Meal Planner"):
    st.session_state.scroll_to_meal_plan = True

if st.sidebar.button("Go to Shopping List"):
    st.session_state.scroll_to_shopping_list = True

# Search button to fetch and display recipes
if st.sidebar.button("Search"):
    if search_term:
        recipes = get_recipes(search_term)
        if recipes:
            display_random_recipes(recipes)  # Display random recipes
        else:
            st.write(f"No recipes found for {search_term}.")
    else:
        st.write("Please enter a search term.")

# Placeholder for Meal Planner
meal_plan_placeholder = st.empty()
meal_plan_placeholder.markdown("## Meal Planner")
# Code for displaying meal planner would go here

# Placeholder for Shopping List
shopping_list_placeholder = st.empty()
shopping_list_placeholder.markdown("## Shopping List")
# Code for generating the shopping list would go here

# Scroll to the Meal Planner if the button was clicked
if "scroll_to_meal_plan" in st.session_state and st.session_state.scroll_to_meal_plan:
    meal_plan_placeholder.empty()
    st.write("## Meal Planner")
    st.session_state.scroll_to_meal_plan = False

# Scroll to the Shopping List if the button was clicked
if "scroll_to_shopping_list" in st.session_state and st.session_state.scroll_to_shopping_list:
    shopping_list_placeholder.empty()
    st.write("## Shopping List")
    st.session_state.scroll_to_shopping_list = False
