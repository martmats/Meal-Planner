import streamlit as st
import requests
import pandas as pd
import io

# Set page configuration
st.set_page_config(page_title="Menu Planner", page_icon="🍽️", layout="wide")

# Custom CSS for styling
st.markdown(
    """
    <style>
        /* Sidebar styling */
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
            background-color: #007bff;
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 10px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
        }

        /* Recipe cards styling */
        .recipe-container {
            border: 2px solid #d4d4d4;
            padding: 20px;
            border-radius: 10px;
            background-color: white;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 40px;  /* Increased spacing between cards */
            width: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .recipe-container img {
            border-radius: 10px;
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

# Search box input (moved to the top of the sidebar)
query = st.sidebar.text_input("Search for recipes (e.g., chicken, vegan pasta)", "dinner")

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

# Function to clear cached results
def clear_recipe_cache():
    if "recipes" in st.session_state:
        del st.session_state["recipes"]
    if "next_page_url" in st.session_state:
        del st.session_state["next_page_url"]

# Function to fetch recipes while adhering to API v2 rules
def fetch_recipes(query, diet_type, calorie_limit, next_page=None):
    if next_page:
        url = next_page  # Use the pre-constructed URL for the next page
        params = None
    else:
        url = "https://api.edamam.com/api/recipes/v2"
        # Build the query parameters for the first page
        params = {
            "type": "public",  # Mandatory parameter
            "q": query,  # Search query
            "app_id": st.secrets["app_id"],  # Your App ID
            "app_key": st.secrets["app_key"],  # Your App Key
        }
        # Add optional filters
        if diet_type != "None":
            params["diet"] = diet_type.lower()
        if calorie_limit > 0:
            params["calories"] = f"lte {calorie_limit}"

    # Send the API request
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        recipes = data.get("hits", [])
        
        # Save the next page URL if available
        next_page_url = data["_links"].get("next", {}).get("href", None)
        st.session_state.next_page_url = next_page_url
        
        return recipes
    else:
        st.error(f"API request failed with status code {response.status_code}")
        st.write(response.text)
        return []

# Clear previous results if the search button is clicked
if st.sidebar.button("Search Recipes"):
    clear_recipe_cache()
    st.session_state.recipes = fetch_recipes(query, diet_type, calorie_limit)

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
        st.markdown('<div id="meal-plan"></div>', unsafe_allow_html=True)
        st.write(f"## Showing {len(recipes)} recipes for **{query}**")
        cols = st.columns(5)  # 5 columns in a row
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

            with cols[idx % 5]:  # Switch to 5 columns
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
st.markdown('<div id="shopping-list"></div>', unsafe_allow_html=True)
st.write("## Your Meal Plan")
cols = st.columns(7)
for idx, (day, meals) in enumerate(st.session_state.meal_plan.items()):
    with cols[idx % 7]:
        st.write(f"### {day}")
        if meals:
            for meal in meals:
                # Handle missing '_links.self.href' when displaying the meal plan
                recipe_url = meal.get('_links', {}).get('self', {}).get('href', '#')
                st.write(f"- [{meal['label']}]({recipe_url}) ({meal['calories']:.0f} calories)")
        else:
            st.write("No meals added yet.")

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
    st.markdown('<div class="shopping-list"></div>', unsafe_allow_html=True)
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


