import streamlit as st
import requests
import pandas as pd
import io

# Set page configuration
st.set_page_config(page_title="Meal Plan Generator", page_icon="🍽️", layout="wide")

# CSS Styling: Sidebar Color, Recipe Card Styling with Border
st.markdown("""
    <style>
        .stApp {{
            background-color: white;
        }}
        /* Sidebar color */
        [data-testid="stSidebar"] {{
            background-color: #93B6F2;
        }}
        /* Style the buttons to be blue */
        .stButton > button {{
            background-color: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            margin-top: 10px;
        }}
        /* Style the recipe cards with a border */
        .recipe-container {{
            border: 1px solid #e0e0e0;
            padding: 10px;
            border-radius: 8px;
            background-color: white;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            margin-bottom: 20px;
            width: 100%;
        }}

        .recipe-container img {{
            border-radius: 8px;
            width: 100%;
            height: 200px;
            object-fit: cover;
        }}
        .recipe-container button {{
            background-color: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            margin-top: 10px;
        }}
    </style>
    """, unsafe_allow_html=True)

# Initialize the meal plan to persist data using session state
if "meal_plan" not in st.session_state:
    st.session_state.meal_plan = {f"Day {i+1}": [] for i in range(7)}

# Sidebar options for search filters and search query
st.sidebar.title("Meal Plan Options")
diet_type = st.sidebar.selectbox("Select Diet", ["Balanced", "Low-Carb", "High-Protein", "None"], index=0)
calorie_limit = st.sidebar.number_input("Max Calories (Optional)", min_value=0, step=50)
query = st.sidebar.text_input("Search for recipes (e.g., chicken, vegan pasta)", "dinner")
if st.sidebar.button("Search Recipes"):
    st.session_state.recipes = fetch_recipes(query, diet_type, calorie_limit)

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
                st.session_state.selected_days[recipe_key] = "Day 1"

            with cols[idx % 5]:  # Switch to 5 columns
                st.markdown(f"""
                <div class="recipe-container">
                    <img src="{recipe['image']}" alt="Recipe Image"/>
                    <h4>{recipe['label']}</h4>
                    <p>Calories: {recipe['calories']:.0f}</p>
                    <a href="{recipe['url']}" target="_blank"><button>View Recipe</button></a>
                </div>
                """, unsafe_allow_html=True)

                selected_day = st.selectbox(
                    f"Choose day for {recipe['label']}",
                    list(st.session_state.meal_plan.keys()), 
                    key=f"day_{recipe_key}"
                )
                if st.button(f"Add {recipe['label']} to {selected_day}", key=f"btn_{idx}"):
                    add_recipe_to_day(selected_day, recipe)

# Display the meal plan in a calendar-like format with recipe URL
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
