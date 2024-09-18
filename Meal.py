import streamlit as st
import requests

# Set up API credentials directly from secrets without nested keys
EDAMAM_APP_ID = st.secrets["app_id"]
EDAMAM_APP_KEY = st.secrets["app_key"]

# API endpoint for Edamam Recipes API
BASE_URL = "https://api.edamam.com/api/recipes/v2"

# Sidebar options for search filters
st.sidebar.title("Meal Plan Options")
meal_type = st.sidebar.selectbox("Select Meal Type", ["Breakfast", "Lunch", "Dinner"], index=2)
diet_type = st.sidebar.selectbox("Select Diet", ["Balanced", "Low-Carb", "High-Protein", "None"], index=0)
calorie_limit = st.sidebar.number_input("Max Calories (Optional)", min_value=0, step=50)

# Input field for the search query
query = st.text_input("Search for recipes (e.g., chicken, vegan pasta)", "dinner")

# Add a button to search
if st.button("Search Recipes"):
    # Build the query parameters for the API request
    params = {
        "type": "public",
        "q": query,
        "app_id": EDAMAM_APP_ID,
        "app_key": EDAMAM_APP_KEY,
        "mealType": meal_type,
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
            # Loop through recipes and display in cards
            for recipe_data in recipes:
                recipe = recipe_data["recipe"]
                st.image(recipe["image"], width=200)
                st.write(f"**{recipe['label']}**")
                st.write(f"Calories: {recipe['calories']:.0f}")
                st.write(f"[View Recipe]({recipe['url']})")
                st.write("---")
        else:
            st.warning("No recipes found. Try adjusting your search.")
    else:
        st.error(f"API request failed with status code {response.status_code}")
        st.write(response.text)
