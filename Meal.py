import streamlit as st
import requests
import pandas as pd
import io

# Set page configuration
st.set_page_config(page_title="Menu Planner", page_icon="🍽️", layout="wide")

# CSS Styling: Sidebar Color, Recipe Card Styling with Border, Hover effect, and Button styles
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
        /* Sidebar title styling */
        h1.menu-title {
            font-size: 24px;
            color: white;
            padding-left: 10px;
            padding-top: 10px;
            text-align: center;
        }
        /* Style the buttons to be blue and bigger with padding */
        .stButton > button {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 15px;
        }
        /* Style the recipe cards with a border, shadow, and padding */
        .recipe-container {
            border: 1px solid #d4d4d4;
            padding: 20px;
            border-radius: 8px;
            background-color: white;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            margin-bottom: 30px; /* Increased margin for spacing */
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
        /* Style View Recipe button inside recipe container */
        .recipe-container button {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 15px;
            margin-top: 10px;
        }
        /* Add spacing between columns */
        div[class*="stColumn"] {
            padding-right: 15px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar title and icon
st.sidebar.markdown('<h1 class="menu-title">🍽️ Menu Planner</h1>', unsafe_allow_html=True)

# Search input field at the top of the sidebar
query = st.sidebar.text_input("Search for recipes (e.g., chicken, vegan pasta)", "dinner")
diet_type = st.sidebar.selectbox("Select Diet", ["Balanced", "Low-Carb", "High-Protein", "None"], index=0)
calorie_limit = st.sidebar.number_input("Max Calories (Optional)", min_value=0, step=50)

# Button to search for recipes
if st.sidebar.button("Search Recipes"):
    clear_recipe_cache()
    st.session_state.recipes = fetch_recipes(query, diet_type, calorie_limit)

# Add buttons for quick navigation to Menu Planner and Shopping List sections
if st.sidebar.button("Go to Menu Planner"):
    st.session_state["scroll_position"] = "menu_planner"

if st.sidebar.button("Go to Shopping List"):
    st.session_state["scroll_position"] = "shopping_list"

# Button to fetch the next page of recipes if available
if "next_page_url" in st.session_state and st.session_state.next_page_url:
    if st.sidebar.button("Load More Recipes"):
        new_recipes = fetch_recipes(query, diet_type, calorie_limit, st.session_state.next_page_url)
        st.session_state.recipes.extend(new_recipes)

# Helper function to add recipes to the meal plan
def add_recipe_to_day(day, recipe):
    st.session_state.meal_plan[day].append(recipe)

# Show recipes if search has been performed
if "recipes" in st.session_state:
    recipes = st.session_state.recipes
    if recipes:
        st.write(f"## Showing {len(recipes)} recipes for **{query}**")
        cols = st.columns(4)  # Display 4 columns per row for recipes
        for idx, recipe_data in enumerate(recipes):
            recipe = recipe_data["recipe"]
            recipe_key = f"recipe_{idx}"
            if recipe_key not in st.session_state.selected_days:
                st.session_state.selected_days[recipe_key] = "Monday"

            # Safely handle missing '_links.self.href'
            recipe_url = recipe.get('_links', {}).get('self', {}).get('href', '#')
            if recipe_url != '#':  # Only show the button if the URL exists
                view_recipe_button = f'<a href="{recipe_url}" target="_blank"><button>View Recipe</button></a>'
            else:
                view_recipe_button = ''

            with cols[idx % 4]:  # Switch to 4 columns
                st.markdown(f"""
                <div class="recipe-container">
                    <img src="{recipe['image']}" alt="Recipe Image"/>
                    <h4>{recipe['label']}</h4>
                    <p>Calories: {recipe['calories']:.0f}</p>
                    {view_recipe_button}
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
if "scroll_position" not in st.session_state or st.session_state["scroll_position"] == "menu_planner":
    st.write("## Your Meal Plan")
    cols = st.columns(7)
    for idx, (day, meals) in enumerate(st.session_state.meal_plan.items()):
        with cols[idx % 7]:
            st.write(f"### {day}")
            if meals:
                for meal in meals:
                    recipe_url = meal.get('_links', {}).get('self', {}).get('href', '#')
                    st.write(f"- [{meal['label']}]({recipe_url}) ({meal['calories']:.0f} calories)")
            else:
                st.write("No meals added yet.")

# Input for number of people before generating the shopping list
people = st.sidebar.number_input("How many people?", min_value=1, value=1)

# Shopping list section
if "scroll_position" not in st.session_state or st.session_state["scroll_position"] == "shopping_list":
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
                [{"Recipe": meal['label'], "Calories": meal['calories'], "URL": meal.get('_links', {}).get('self', {}).get('href', '#')} for meal in meals]
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

