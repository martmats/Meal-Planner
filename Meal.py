import streamlit as st
import requests

# Set page configuration
st.set_page_config(page_title="Meal Plan Generator", page_icon="🍽️", layout="wide")

# Apply a blue theme for the sidebar
st.markdown("""
    <style>
        body {
            background-color: #f0f8ff;
        }
        .stApp {
            background-color: #f0f8ff;
        }
        .css-18e3th9 {
            background-color: #007bff;
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

# Initialize session state for the meal plan to persist data
if "meal_plan" not in st.session_state:
    st.session_state.meal_plan = {f"Day {i+1}": [] for i in range(7)}

# API endpoint for Edamam Recipes API
BASE_URL = "https://api.edamam.com/api/recipes/v2"

# Sidebar options
st.sidebar.title("Meal Plan Options")
diet_type = st.sidebar.selectbox("Select Diet", ["Balanced", "Low-Carb", "High-Protein", "None"], index=0)
calorie_limit = st.sidebar.number_input("Max Calories (Optional)", min_value=0, step=50)

# Input field for the search query
query = st.text_input("Search for recipes (e.g., chicken, vegan pasta)", "dinner")

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

            # Display recipes in card format with 3 columns
            cols = st.columns(3)
            for idx, recipe_data in enumerate(recipes):
                recipe = recipe_data["recipe"]
                with cols[idx % 3]:
                    st.image(recipe["image"], use_column_width=True)
                    st.write(f"**{recipe['label']}**")
                    st.write(f"Calories: {recipe['calories']:.0f}")
                    st.write(f"[View Recipe]({recipe['url']})")
                    chosen_day = st.selectbox(f"Add to which day?", list(st.session_state.meal_plan.keys()), key=f"day_{idx}")
                    if st.button(f"Add {recipe['label']} to {chosen_day}", key=f"btn_{idx}"):
                        st.session_state.meal_plan[chosen_day].append(recipe)

        else:
            st.warning("No recipes found. Try adjusting your search.")
    else:
        st.error(f"API request failed with status code {response.status_code}")
        st.write(response.text)

# Display the meal plan in a calendar-like format
st.write("## Your Meal Plan")

cols = st.columns(7)  # Display days in a 7-column format (calendar style)
for idx, (day, meals) in enumerate(st.session_state.meal_plan.items()):
    with cols[idx % 7]:
        st.write(f"### {day}")
        if meals:
            for meal in meals:
                st.write(f"- {meal['label']} ({meal['calories']:.0f} calories)")
        else:
            st.write("No meals added yet.")

# Generate shopping list
if st.button("Generate Shopping List"):
    shopping_list = {}
    for meals in st.session_state.meal_plan.values():
        for recipe in meals:
            for ingredient in recipe["ingredients"]:
                if ingredient["food"] in shopping_list:
                    shopping_list[ingredient["food"]] += ingredient["quantity"]
                else:
                    shopping_list[ingredient["food"]] = ingredient["quantity"]

    # Display the shopping list
    st.write("## Shopping List")
    for food, quantity in shopping_list.items():
        st.write(f"{food}: {quantity}")

