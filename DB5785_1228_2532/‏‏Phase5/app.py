import streamlit as st
from ui_components import (
    login_page, home_page, run_routines, show_database_statistics, show_settings, show_queries, show_main_programs
)
from database_manager import DatabaseManager
from utils import authenticate_user, logout
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page configuration
st.set_page_config(
    page_title="Dormitory Management System",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = None
if 'connection_string' not in st.session_state:
    st.session_state.connection_string = ""
if 'current_page' not in st.session_state:
    st.session_state.current_page = "login"
if 'selected_table' not in st.session_state:
    st.session_state.selected_table = None
if 'table_operation' not in st.session_state:
    st.session_state.table_operation = "View"  # Default to View

def main():
    """Main application function"""
    if not st.session_state.authenticated:
        login_page()
    else:
        if st.session_state.current_page == "home":
            home_page()
        elif st.session_state.current_page == "routines":
            run_routines()
        elif st.session_state.current_page == "statistics":
            show_database_statistics()
        elif st.session_state.current_page == "settings":
            show_settings()
        elif st.session_state.current_page == "queries":
            show_queries()
        elif st.session_state.current_page == "main_programs":
            show_main_programs()

if __name__ == "__main__":
    main()