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

# Rest of your code for the menu planner functionality, recipe fetching, and shopping list
