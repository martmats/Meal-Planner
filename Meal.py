import streamlit as st
import requests
import os

# Set page configuration
st.set_page_config(page_title="Meal Plan Generator", page_icon="🍽️", layout="wide")

# Apply a blue theme to the app
st.markdown("""
    <style>
        body {
            background-color: #f0f8ff;
        }
        .stApp {
            background-color: #e0f2ff;
        }
        .stButton > button {
            background-color: #007bff;
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)

# API credentials from Streamlit Secrets (already added in secrets.toml)
EDAMAM_APP_ID = st.secrets["app_id"]
EDAMAM_APP_KEY = st.secrets["app_key"]

# API endpoint for Edamam Recipes API
BASE_URL = "https://api.edamam.com/api/recipes/v2"

# Sidebar options for search filters
st.sidebar.title("Meal Plan Generator")
num_days = st.sidebar.selectbox("Select number of days", [7, 14, 30], index=0)
diet_type = st.sidebar.selectbox("Select Diet", ["Balanced", "Low-Carb", "High-Protein", "None"], index=0)
calorie_limit = st.sidebar.number_input("Max Calories (Optional)", min_value=0, step=50)

# Input field for the search query
query = st.text_input("Search for recipes (e.g., chicken, vegan pasta)", "dinner")

# A dictionary to store meal plans for each day
meal_plan = {f"Day {i+1}": [] for i in range(num_days)}

# Search button
if st.button("Search Recipes"):
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
        recipes = response.json().get("hits", [])

        if recipes:
            st.write(f"## Showing {len(recipes)} recipes for **{query}**")

            # Create a container for the rows
            container = st.container()
            columns = st.columns(3)  # Display recipes in 3 columns (row format)

            # Display recipes in row format (3 columns per row)
            for idx, recipe_data in enumerate(recipes):
                recipe = recipe_data["recipe"]
                col_idx = idx % 3  # Display 3 items per row
                with columns[col_idx]:
                    st.image(recipe["image"], width=200)
                    st.write(f"**{recipe['label']}**")
                    st.write(f"Calories: {recipe['calories']:.0f}")
                    st.write(f"[View Recipe]({recipe['url']})")
                    # Option to add recipe to the meal plan for a specific day
                    chosen_day = st.selectbox(f"Add to which day?", list(meal_plan.keys()), key=recipe['label'])
                    if st.button(f"Add {recipe['label']} to {chosen_day}", key=f"btn_{recipe['label']}"):
                        meal_plan[chosen_day].append(recipe)
            st.write("---")
        else:
            st.warning("No recipes found. Try adjusting your search.")
    else:
        st.error(f"API request failed with status code {response.status_code}")
        st.write(response.text)

# Display the meal plan
st.write("## Your Meal Plan")
for day, meals in meal_plan.items():
    st.write(f"### {day}")
    if meals:
        for meal in meals:
            st.write(f"- {meal['label']} ({meal['calories']:.0f} calories)")
    else:
        st.write("No meals added yet.")

# Button to generate a shopping list based on the meal plan
if st.button("Generate Shopping List"):
    # Combine ingredients for all recipes
    shopping_list = {}
    for meals in meal_plan.values():
        for recipe in meals:
            for ingredient in recipe["ingredients"]:
                if ingredient["food"] in shopping_list:
                    shopping_list[ingredient["food"]] += ingredient["quantity"]
                else:
                    shopping_list[ingredient["food"]] = ingredient["quantity"]

    # Display shopping list
    st.write("## Shopping List")
    for food, quantity in shopping_list.items():
        st.write(f"{food}: {quantity}")

