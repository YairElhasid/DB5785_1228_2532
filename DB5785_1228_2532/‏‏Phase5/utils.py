import streamlit as st
from database_manager import DatabaseManager
import logging

# Configure logging
logger = logging.getLogger(__name__)

def authenticate_user(username: str, password: str, host: str = "localhost", port: str = "5432", database: str = "mydatabase") -> bool:
    """Authenticate user"""
    try:
        connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"
        db_manager = DatabaseManager()
        if db_manager.connect(connection_string):
            st.session_state.db_manager = db_manager
            st.session_state.connection_string = connection_string
            st.session_state.authenticated = True
            return True
        else:
            return False
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        return False

def logout():
    """Log out from the system"""
    if st.session_state.db_manager:
        st.session_state.db_manager.close()
    st.session_state.authenticated = False
    st.session_state.db_manager = None
    st.session_state.connection_string = ""
    st.session_state.current_page = "login"
    st.session_state.selected_table = None
    st.session_state.table_operation = "View"
    st.rerun()