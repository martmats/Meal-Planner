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

# Initialize the current search state, including page number and previous results
if "search_results" not in st.session_state:
    st.session_state.search_results = []
if "current_page" not in st.session_state:
    st.session_state.current_page = random.randint(1, 10)  # Start with a random page number

# API request function with page support
def search_recipes(query, page):
    api_url = f"https://api.edamam.com/search?q={query}&page={page}&app_id=YOUR_APP_ID&app_key=YOUR_APP_KEY"
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch recipes.")
        return None

# Randomize the page number again on every new search click to get fresh results
user_query = st.text_input("Enter a meal keyword")

# When the user clicks search
if st.button("Search"):
    if user_query:
        # Reset search results and page number on new search
        st.session_state.search_results = []
        st.session_state.current_page = random.randint(1, 10)
        
        # Fetch initial page results
        search_results = search_recipes(user_query, st.session_state.current_page)
        
        if search_results:
            st.session_state.search_results.extend(search_results.get("hits", []))
        else:
            st.write("No recipes found.")

# Show the recipes after search
if st.session_state.search_results:
    st.write("## Recipe Results")
    for recipe in st.session_state.search_results:
        recipe_data = recipe["recipe"]
        st.markdown(f"### {recipe_data['label']}")
        st.image(recipe_data['image'], use_column_width=True)
        st.markdown(f"[View Recipe]({recipe_data['url']})")
        st.write(f"Calories: {recipe_data['calories']:.0f}")
        
    # "Load More Results" button
    if st.button("Load More Results"):
        # Increment page number for fetching more results
        st.session_state.current_page += 1
        additional_results = search_recipes(user_query, st.session_state.current_page)
        
        if additional_results:
            st.session_state.search_results.extend(additional_results.get("hits", []))
        else:
            st.write("No more results.")

else:
    st.write("Press the Search button to get recipes.")

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

# Function to download meal plans as CSV
def download_meal_plan():
    output = io.StringIO()  # Use in-memory string buffer for CSV format
    for day, meals in st.session_state.meal_plan.items():
        if meals:
            day_meals = pd.DataFrame(
                [{"Recipe": meal['label'], "Calories": meal['calories'], "URL": meal['url']} for meal in meals]
            )
            output.write(f"\n{day}\n")
            day_meals.to_csv(output, index=False)

    # Ensure the buffer is ready for download
    output.seek(0)
    return output

# Button to download meal plan as a CSV file
if st.button("Download Meal Plan as CSV"):
    csv_data = download_meal_plan()
    st.download_button(
        label="Download CSV File",
        data=csv_data.getvalue(),  # Fix for correct data format
        file_name="meal_plan.csv",
        mime="text/csv"
    )
