import streamlit as st
import pandas as pd
from datetime import datetime, date
from typing import List, Dict, Any
import uuid
from database_manager import DatabaseManager
from utils import authenticate_user, logout
import re
from sqlalchemy import text
import os
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.extras import RealDictCursor

def is_date_field(col_name: str) -> bool:
    return 'date' in col_name.lower()

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number format"""
    pattern = r'^\+972 5\d-\d{3}-\d{4}$'
    return re.match(pattern, phone) is not None

def validate_name(name):
    """Validate name - only letters and spaces"""
    pattern = r'^[a-zA-Z\s]+$'
    return re.match(pattern, name) is not None and len(name.strip()) > 0

def validate_major(major):
    return major in ['Computer Science', 'Mathematics', 'Physics', 'Biology', 'Chemistry']

def get_field_type(table_name, field_name):
    """Get the type of field for specific validation"""
    field_types = {
        'dorm_management': {
            'firstname': 'name',
            'lastname': 'name',
            'gender': 'gender',
            'phonenumber': 'phone',
            'email': 'email'
        },
        'student': {
            'firstname': 'name',
            'lastname': 'name',
            'gender': 'gender',
            'phonenumber': 'phone',
            'email': 'email',
            'major': 'major'
        },
        'lease': {
            'discountpercent': 'discount'
        },
        'maintenance_request': {
            'priority': 'priority'
        }
    }
    return field_types.get(table_name, {}).get(field_name.lower(), 'text')

def render_navigation_buttons():
    """Render navigation buttons at the top of the page"""
    st.markdown('<div class="nav-buttons">', unsafe_allow_html=True)
    cols = st.columns(7)
    with cols[0]:
        if st.button("🏠 Home", key="nav_home", use_container_width=True):
            st.session_state.current_page = "home"
            st.session_state.table_operation = "View"
            st.rerun()
    with cols[1]:
        if st.button("⚙️ Routines", key="nav_routines", use_container_width=True):
            st.session_state.current_page = "routines"
            st.session_state.table_operation = None
            st.rerun()
    with cols[2]:
        if st.button("📊 Statistics", key="nav_statistics", use_container_width=True):
            st.session_state.current_page = "statistics"
            st.session_state.table_operation = None
            st.rerun()
    with cols[3]:
        if st.button("🔧 Settings", key="nav_settings", use_container_width=True):
            st.session_state.current_page = "settings"
            st.session_state.table_operation = None
            st.rerun()
    with cols[4]:
        if st.button("📋 Queries", key="nav_queries", use_container_width=True):
            st.session_state.current_page = "queries"
            st.session_state.table_operation = None
            st.rerun()
    with cols[5]:
        if st.button("📚 Mains", key="nav_main_programs", use_container_width=True):
            st.session_state.current_page = "main_programs"
            st.session_state.table_operation = None
            st.rerun()
    with cols[6]:
        if st.button("🚪 Logout", key="logout_button", use_container_width=True):
            logout()
    st.markdown('</div>', unsafe_allow_html=True)

def render_action_buttons():
    """Render action buttons for table operations"""
    st.markdown('<div class="action-buttons">', unsafe_allow_html=True)
    cols = st.columns(4)
    with cols[0]:
        if st.button("👀 View", key="view_button", use_container_width=True,
                     type="primary" if st.session_state.table_operation == "View" else "secondary"):
            st.session_state.table_operation = "View"
            if 'selected_records' in st.session_state:
                del st.session_state.selected_records
            st.rerun()
    with cols[1]:
        if st.button("➕ Add", key="add_button", use_container_width=True,
                     type="primary" if st.session_state.table_operation == "Add" else "secondary"):
            st.session_state.table_operation = "Add"
            if 'selected_records' in st.session_state:
                del st.session_state.selected_records
            st.rerun()
    with cols[2]:
        if st.button("✏️ Edit", key="edit_button", use_container_width=True,
                     type="primary" if st.session_state.table_operation == "Edit" else "secondary"):
            st.session_state.table_operation = "Edit"
            if 'selected_records' in st.session_state:
                del st.session_state.selected_records
            st.rerun()
    with cols[3]:
        if st.button("🗑️ Delete", key="delete_button", use_container_width=True,
                     type="primary" if st.session_state.table_operation == "Delete" else "secondary"):
            st.session_state.table_operation = "Delete"
            if 'selected_records' in st.session_state:
                del st.session_state.selected_records
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def render_back_to_home_button():
    """Render a Back to Home button"""
    if st.button("🏠 Back to Home", key="back_to_home", use_container_width=True):
        st.session_state.current_page = "home"
        st.session_state.table_operation = "View"
        if 'selected_records' in st.session_state:
            del st.session_state.selected_records
        st.rerun()

def login_page():
    """Login page"""
    st.markdown('<div class="ltr">', unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">🗄️ Database Management System</h1>', unsafe_allow_html=True)
    with st.container():
        st.markdown("### 🔐 System Login")
        col1, col2 = st.columns(2)
        with col1:
            host = st.text_input("🖥️ Server Address", value="localhost", key="host")
            database = st.text_input("🗄️ Database Name", value="mydatabase", key="database")
        with col2:
            port = st.text_input("🔌 Port", value="5432", key="port")
            username = st.text_input("👤 Username", key="username")
        password = st.text_input("🔑 Password", type="password", key="password")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚪 Login", use_container_width=True):
                if username and password:
                    with st.spinner("Connecting..."):
                        if authenticate_user(username, password, host, port, database):
                            st.success("✅ Login successful")
                            st.session_state.current_page = "home"
                            st.rerun()
                        else:
                            st.error("❌ Login failed. Please check your credentials.")
                else:
                    st.warning("⚠️ Please enter username and password.")
    st.markdown('</div>', unsafe_allow_html=True)

def home_page():
    """Home page with table selection and action buttons"""
    st.markdown('<div class="ltr">', unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">🗄️ Database Management System</h1>', unsafe_allow_html=True)
    render_navigation_buttons()
    st.markdown("### 📋 Table Management")
    if st.session_state.db_manager:
        tables = st.session_state.db_manager.get_table_names()
        if tables:
            col1, col2 = st.columns([2, 5])
            with col1:
                st.session_state.selected_table = st.selectbox(
                    "📊 Select Table",
                    options=tables,
                    key="selected_table_home",
                    index=tables.index(st.session_state.selected_table) if st.session_state.selected_table in tables else 0
                )
            with col2:
                render_action_buttons()
            if st.session_state.selected_table:
                if st.session_state.table_operation == "View":
                    view_table_data(st.session_state.selected_table)
                elif st.session_state.table_operation == "Add":
                    add_record(st.session_state.selected_table)
                elif st.session_state.table_operation == "Edit":
                    edit_record(st.session_state.selected_table)
                elif st.session_state.table_operation == "Delete":
                    delete_record(st.session_state.selected_table)
        else:
            st.error("❌ No tables found in the system.")
    else:
        st.error("❌ Error connecting to the system.")
    st.markdown('</div>', unsafe_allow_html=True)

def view_table_data(table_name: str):
    """View table data"""
    st.markdown(f"### 📊 Table Data: {table_name}")
    table_info = st.session_state.db_manager.get_table_info(table_name)
    if table_info:
        with st.expander("ℹ️ Table Information"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Columns:**")
                for col in table_info['columns']:
                    st.write(f"- {col['name']} ({col['type']})")
            with col2:
                if table_info['primary_keys']['constrained_columns']:
                    st.markdown("**Primary Keys:**")
                    for pk in table_info['primary_keys']['constrained_columns']:
                        st.write(f"• {pk}")
    col1, col2 = st.columns([1, 3])
    with col1:
        limit = st.number_input("Number of Records", min_value=1, max_value=90000, value=10000, key=f"limit_{table_name}")
    with col2:
        if st.button("🔄 Refresh Data", key=f"refresh_{table_name}"):
            st.rerun()
    data = st.session_state.db_manager.get_table_data(table_name, limit)
    if not data.empty:
        st.dataframe(data, use_container_width=True, height=400)
        st.markdown(f"**Found {len(data)} records**")
        csv = data.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"{table_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("ℹ️ No data found in the table.")

def add_record(table_name: str):
    """Add a new record"""
    st.markdown(f"### ➕ Add New Record to Table: {table_name}")
    table_info = st.session_state.db_manager.get_table_info(table_name)
    primary_keys = table_info['primary_keys']['constrained_columns']
    if not table_info:
        st.error("❌ Unable to retrieve table information.")
        render_back_to_home_button()
        return
    if not primary_keys:
        st.error("❌ Cannot add to table without a primary key.")
        render_back_to_home_button()
        return
    with st.form(f"add_form_{table_name}"):
        st.markdown("**📝 Enter New Data:**")
        form_data = {}
        validation_errors = []
        for col in table_info['columns']:
            col_name = col['name']
            col_type = str(col['type']).lower()
            nullable = col.get('nullable', True)
            is_auto_increment = col.get('autoincrement', False)
            if is_auto_increment:
                try:
                    from sqlalchemy import text
                    max_id_query = text(f"SELECT MAX({col_name}) FROM {table_name}")
                    with st.session_state.db_manager.engine.connect() as conn:
                        result = conn.execute(max_id_query).fetchone()
                        max_id = result[0] if result[0] is not None else 0
                        next_id = max_id + 1
                        form_data[col_name] = next_id
                        st.info(f"🔢 {col_name} (Auto-generated) - Next ID: {next_id}")
                except Exception as e:
                    st.error(f"❌ Failed to generate ID for {col_name}: {str(e)}")
                    form_data[col_name] = 1
                    st.warning(f"⚠️ Using default ID: 1 for {col_name}")
                continue
            if 'int' in col_type:
                value = st.number_input(
                    f"{col_name} ({'Required' if not nullable else 'Optional'})",
                    value=None if nullable else 0,
                    key=f"add_{col_name}_{table_name}",
                    step=1
                )
                if value is not None:
                    form_data[col_name] = int(value)
            elif 'float' in col_type or 'numeric' in col_type or 'decimal' in col_type:
                value = st.number_input(
                    f"{col_name} ({'Required' if not nullable else 'Optional'})",
                    value=None if nullable else 0.0,
                    key=f"add_{col_name}_{table_name}",
                    step=0.01
                )
                if value is not None:
                    form_data[col_name] = float(value)
            elif 'bool' in col_type:
                value = st.checkbox(
                    f"{col_name}",
                    key=f"add_{col_name}_{table_name}"
                )
                form_data[col_name] = value
            elif is_date_field(col_name):
                default_date = None if nullable else date.today()
                value = st.date_input(
                    f"📅 {col_name} ({'Required' if not nullable else 'Optional'})",
                    value=default_date,
                    key=f"add_{col_name}_{table_name}"
                )
                if value is not None:
                    form_data[col_name] = value
            else:
                field_type = get_field_type(table_name, col_name)
                if field_type == 'gender':
                    value = st.selectbox(
                        f"👤 {col_name} ({'Required' if not nullable else 'Optional'})",
                        options=['', 'Male', 'Female'] if nullable else ['Male', 'Female'],
                        key=f"add_{col_name}_{table_name}"
                    )
                    if value:
                        form_data[col_name] = value
                elif field_type == 'priority':
                    value = st.selectbox(
                        f"🔥 {col_name} ({'Required' if not nullable else 'Optional'})",
                        options=['', 'Low', 'Medium', 'High'] if nullable else ['Low', 'Medium', 'High'],
                        key=f"add_{col_name}_{table_name}"
                    )
                    if value:
                        form_data[col_name] = value
                elif field_type == 'discount':
                    value = st.number_input(
                        f"💰 {col_name} (%) ({'Required' if not nullable else 'Optional'})",
                        min_value=0.0,
                        max_value=100.0,
                        value=0.0 if not nullable else None,
                        step=0.1,
                        key=f"add_{col_name}_{table_name}"
                    )
                elif field_type == 'major':
                    value = st.selectbox(
                        f"🎓 {col_name} ({'Required' if not nullable else 'Optional'})",
                        options=['', 'Computer Science', 'Mathematics', 'Physics', 'Biology', 'Chemistry'] if nullable else
                        ['Computer Science', 'Mathematics', 'Physics', 'Biology', 'Chemistry'],
                        key=f"add_{col_name}_{table_name}"
                    )
                    if value is not None:
                        form_data[col_name] = value
                else:
                    value = st.text_input(
                        f"📝 {col_name} ({'Required' if not nullable else 'Optional'})",
                        key=f"add_{col_name}_{table_name}"
                    )
                    if field_type == 'phone':
                        st.caption("📞 Format: +972 510-123-4567")
                    elif field_type == 'email':
                        st.caption("📧 Format: user@example.com")
                    elif field_type == 'name':
                        st.caption("👤 Only letters and spaces allowed")
                    if value or not nullable:
                        form_data[col_name] = value
        submitted = st.form_submit_button("✅ Add Record", use_container_width=True)
        if submitted:
            required_fields = [col['name'] for col in table_info['columns']
                               if not col.get('nullable', True) and not col.get('autoincrement', False)]
            missing_fields = [field for field in required_fields if field not in form_data or form_data[field] == '']
            if missing_fields:
                st.error(f"❌ Missing required fields: {', '.join(missing_fields)}")
            else:
                validation_errors = []
                for field, value in form_data.items():
                    if value:
                        field_type = get_field_type(table_name, field)
                        if field_type == 'email' and not validate_email(value):
                            validation_errors.append(f"Invalid email format in: {field}")
                        elif field_type == 'phone' and not validate_phone(value):
                            validation_errors.append(f"Invalid phone format in: {field}")
                        elif field_type == 'name' and not validate_name(value):
                            validation_errors.append(f"Invalid name format in: {field}")
                        elif field_type == 'major' and not validate_major:
                            validation_errors.append(f"Major must be one of: Computer Science, Mathematics, Physics, Biology, Chemistry in: {field}")
                if validation_errors:
                    for error in validation_errors:
                        st.error(f"❌ {error}")
                else:
                    if st.session_state.db_manager.insert_record(table_name, form_data):
                        st.success("✅ Record added successfully!")
                        st.balloons()
                    else:
                        st.error("❌ Error adding record!")
                        st.error("⚠️ Hint: Check forgotten primary key or unique constraints.")
    render_back_to_home_button()

def edit_record(table_name: str):
    """Edit an existing record with integrated selection"""
    st.markdown(f"### ✏️ Edit Record in Table: {table_name}")
    table_info = st.session_state.db_manager.get_table_info(table_name)
    primary_keys = table_info['primary_keys']['constrained_columns']
    if not primary_keys:
        st.error("❌ Cannot edit table without a primary key.")
        render_back_to_home_button()
        return
    data = st.session_state.db_manager.get_table_data(table_name, 1000)
    if data.empty:
        st.info("ℹ️ No records found for editing.")
        render_back_to_home_button()
        return
    st.markdown("**1️⃣ Select Record to Edit:**")
    display_data = data.copy()
    display_data.insert(0, 'Select', False)
    edited_data = st.data_editor(
        display_data,
        use_container_width=True,
        height=400,
        column_config={
            "Select": st.column_config.CheckboxColumn(
                "Select",
                help="Select a record to edit",
                default=False,
            )
        },
        disabled=[col for col in display_data.columns if col != 'Select'],
        hide_index=True,
        key=f"edit_select_{table_name}"
    )
    selected_indices = edited_data[edited_data['Select'] == True].index.tolist()
    if len(selected_indices) == 1:
        selected_index = selected_indices[0]
        selected_row = data.iloc[selected_index]
        with st.container():
            st.markdown("---")
            st.markdown("**2️⃣ Edit Data:**")
            with st.form(f"edit_form_{table_name}_{selected_index}"):
                form_data = {}
                validation_errors = []
                for col in table_info['columns']:
                    col_name = col['name']
                    col_type = str(col['type']).lower()
                    nullable = col.get('nullable', True)
                    current_value = selected_row[col_name]
                    is_auto_increment = col.get('autoincrement', False)
                    if col_name in primary_keys:
                        st.text_input(f"🔑 {col_name} (Primary Key)",
                                      value=str(current_value),
                                      disabled=True,
                                      key=f"edit_pk_{col_name}_{selected_index}")
                        continue
                    if is_auto_increment:
                        st.text_input(f"🔢 {col_name} (Auto-generated)",
                                      value=str(current_value),
                                      disabled=True,
                                      key=f"edit_auto_{col_name}_{selected_index}")
                        continue
                    if 'int' in col_type:
                        value = st.number_input(
                            f"{col_name} ({'Required' if not nullable else 'Optional'})",
                            value=int(current_value) if pd.notna(current_value) else (0 if not nullable else None),
                            key=f"edit_{col_name}_{selected_index}",
                            step=1
                        )
                        if value is not None:
                            form_data[col_name] = int(value)
                    elif 'float' in col_type or 'numeric' in col_type or 'decimal' in col_type:
                        value = st.number_input(
                            f"{col_name} ({'Required' if not nullable else 'Optional'})",
                            value=float(current_value) if pd.notna(current_value) else (0.0 if not nullable else None),
                            key=f"edit_{col_name}_{selected_index}",
                            step=0.01
                        )
                        if value is not None:
                            form_data[col_name] = float(value)
                    elif 'bool' in col_type:
                        value = st.checkbox(
                            f"{col_name}",
                            value=bool(current_value) if pd.notna(current_value) else False,
                            key=f"edit_{col_name}_{selected_index}"
                        )
                        form_data[col_name] = value
                    elif is_date_field(col_name):
                        if pd.notna(current_value):
                            try:
                                if isinstance(current_value, str):
                                    current_date = pd.to_datetime(current_value).date()
                                else:
                                    current_date = current_value.date() if hasattr(current_value, 'date') else current_value
                            except:
                                current_date = date.today() if not nullable else None
                        else:
                            current_date = date.today() if not nullable else None
                        value = st.date_input(
                            f"📅 {col_name} ({'Required' if not nullable else 'Optional'})",
                            value=current_date,
                            key=f"edit_{col_name}_{selected_index}"
                        )
                        if value is not None:
                            form_data[col_name] = value
                    else:
                        field_type = get_field_type(table_name, col_name)
                        current_str_value = str(current_value) if pd.notna(current_value) else ""
                        if field_type == 'gender':
                            gender_options = ['', 'Male', 'Female'] if nullable else ['Male', 'Female']
                            current_index = 0
                            if current_str_value in gender_options:
                                current_index = gender_options.index(current_str_value)
                            value = st.selectbox(
                                f"👤 {col_name} ({'Required' if not nullable else 'Optional'})",
                                options=gender_options,
                                index=current_index,
                                key=f"edit_{col_name}_{selected_index}"
                            )
                            if value:
                                form_data[col_name] = value
                        elif field_type == 'priority':
                            priority_options = ['', 'Low', 'Medium', 'High'] if nullable else ['Low', 'Medium', 'High']
                            current_index = 0
                            if current_str_value in priority_options:
                                current_index = priority_options.index(current_str_value)
                            value = st.selectbox(
                                f"🔥 {col_name} ({'Required' if not nullable else 'Optional'})",
                                options=priority_options,
                                index=current_index,
                                key=f"edit_{col_name}_{selected_index}"
                            )
                            if value:
                                form_data[col_name] = value
                        elif field_type == 'discount':
                            discount_value = float(current_value) if pd.notna(current_value) else (0.0 if not nullable else None)
                            value = st.number_input(
                                f"💰 {col_name} (%) ({'Required' if not nullable else 'Optional'})",
                                min_value=0.0,
                                max_value=100.0,
                                value=discount_value,
                                step=0.1,
                                key=f"edit_{col_name}_{selected_index}"
                            )
                            if value is not None:
                                form_data[col_name] = value
                        elif field_type == 'major':
                            major_options = ['', 'Computer Science', 'Mathematics', 'Physics', 'Biology', 'Chemistry'] if nullable else ['Computer Science', 'Mathematics', 'Physics', 'Biology', 'Chemistry']
                            current_index = 0
                            if current_str_value in major_options:
                                current_index = major_options.index(current_str_value)
                            value = st.selectbox(
                                f"🎓 {col_name} ({'Required' if not nullable else 'Optional'})",
                                options=major_options,
                                index=current_index,
                                key=f"edit_{col_name}_{selected_index}"
                            )
                            if value:
                                form_data[col_name] = value
                        else:
                            value = st.text_input(
                                f"📝 {col_name} ({'Required' if not nullable else 'Optional'})",
                                value=current_str_value,
                                key=f"edit_{col_name}_{selected_index}"
                            )
                            if field_type == 'phone':
                                st.caption("📞 Format: +972 50-123-4567")
                            elif field_type == 'email':
                                st.caption("📧 Format: user@example.com")
                            elif field_type == 'name':
                                st.caption("👤 Only letters and spaces allowed")
                            if value or not nullable:
                                form_data[col_name] = value
                col1, col2 = st.columns(2)
                with col1:
                    submitted = st.form_submit_button("✅ Update Record", use_container_width=True, type="primary")
                with col2:
                    cancelled = st.form_submit_button("❌ Cancel", use_container_width=True)
                if submitted:
                    required_fields = [col['name'] for col in table_info['columns']
                                       if not col.get('nullable', True) and not col.get('autoincrement', False) and col['name'] not in primary_keys]
                    missing_fields = [field for field in required_fields if field not in form_data or form_data[field] == '']
                    if missing_fields:
                        st.error(f"❌ Missing required fields: {', '.join(missing_fields)}")
                    else:
                        validation_errors = []
                        for field, value in form_data.items():
                            if value:
                                field_type = get_field_type(table_name, field)
                                if field_type == 'email' and not validate_email(value):
                                    validation_errors.append(f"Invalid email format in: {field}")
                                elif field_type == 'phone' and not validate_phone(value):
                                    validation_errors.append(f"Invalid phone format in: {field}")
                                elif field_type == 'name' and not validate_name(value):
                                    validation_errors.append(f"Invalid name format in: {field}")
                                elif field_type == 'major' and not validate_major(value):
                                    validation_errors.append(f"Major must be one of: Computer Science, Mathematics, Physics, Biology, Chemistry in: {field}")
                        if validation_errors:
                            for error in validation_errors:
                                st.error(f"❌ {error}")
                        else:
                            record_id = selected_row[primary_keys[0]]
                            if st.session_state.db_manager.update_record(table_name, record_id, form_data, primary_keys[0]):
                                st.success("✅ Record updated successfully!")
                                st.balloons()
                                st.sleep(1)
                                st.rerun()
                            else:
                                st.error("❌ Error updating record")
                                st.error("⚠️ Hint: Check for unique constraints violations.")
                if cancelled:
                    st.session_state.table_operation = "View"
                    st.rerun()
    elif len(selected_indices) > 1:
        st.warning("⚠️ Please select only one record for editing.")
    else:
        st.info("ℹ️ Please select a record to edit.")
    render_back_to_home_button()

def delete_record(table_name: str):
    """Delete a record with integrated selection and confirmation"""
    st.markdown(f"### 🗑️ Delete Record from Table: {table_name}")
    table_info = st.session_state.db_manager.get_table_info(table_name)
    primary_keys = table_info['primary_keys']['constrained_columns']
    if not primary_keys:
        st.error("❌ Cannot delete from table without a primary key.")
        render_back_to_home_button()
        return
    data = st.session_state.db_manager.get_table_data(table_name, 1000)
    if data.empty:
        st.info("ℹ️ No records found for deletion.")
        render_back_to_home_button()
        return
    st.markdown("**1️⃣ Select Records to Delete:**")
    display_data = data.copy()
    display_data.insert(0, 'Select', False)
    edited_data = st.data_editor(
        display_data,
        use_container_width=True,
        height=400,
        column_config={
            "Select": st.column_config.CheckboxColumn(
                "Select",
                help="Select records to delete",
                default=False,
            )
        },
        disabled=[col for col in display_data.columns if col != 'Select'],
        hide_index=True,
        key=f"delete_select_{table_name}"
    )
    selected_indices = edited_data[edited_data['Select'] == True].index.tolist()
    if len(selected_indices) > 0:
        selected_records = data.iloc[selected_indices]
        st.markdown(f"**2️⃣ Selected {len(selected_records)} records for deletion:**")
        st.dataframe(selected_records, use_container_width=True)
        st.markdown("**3️⃣ Confirm Deletion:**")
        st.error("⚠️ **WARNING: This action cannot be undone!**")
        confirm_text = st.text_input(
            "Type 'DELETE' to confirm deletion:",
            key=f"confirm_delete_{table_name}",
            placeholder="Type DELETE here..."
        )
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Delete Records",
                         key=f"delete_records_{table_name}",
                         type="primary",
                         use_container_width=True):
                if confirm_text == "DELETE":
                    with st.spinner("Deleting records..."):
                        success_count = 0
                        for _, row in selected_records.iterrows():
                            record_id = row[primary_keys[0]]
                            if st.session_state.db_manager.delete_record(table_name, record_id, primary_keys[0]):
                                success_count += 1
                        if success_count == len(selected_records):
                            st.success(f"✅ {success_count} records deleted successfully!")
                            st.rerun()
                        else:
                            st.error(f"❌ {success_count} out of {len(selected_records)} records deleted successfully")
                else:
                    st.error("❌ Incorrect confirmation. Type 'DELETE' exactly.")
        with col2:
            if st.button("❌ Cancel",
                         key=f"cancel_delete_{table_name}",
                         use_container_width=True):
                st.session_state.table_operation = "View"
                st.rerun()
    else:
        st.info("ℹ️ Please select records to delete.")
    render_back_to_home_button()

def run_routines():
    """Screen to run procedures and functions with enhanced support for REF CURSOR and NOTICE"""
    st.markdown('<div class="ltr">', unsafe_allow_html=True)
    st.markdown("### ⚙️ Run Procedures and Functions")
    render_navigation_buttons()
    refcursor_FLAG = False
    def set_refcursor_FLAG(value):
        """Set the REF CURSOR flag in session state"""
        nonlocal refcursor_FLAG
        refcursor_FLAG = value
    routines = st.session_state.db_manager.get_routines()
    if not routines:
        st.error("❌ No procedures or functions found.")
        render_back_to_home_button()
        st.markdown('</div>', unsafe_allow_html=True)
        return
    for routine in routines:
        routine_name = routine['routine_name']
        routine_type = routine['routine_type']
        specific_name = routine['specific_name']
        icon = "📋" if routine_type == 'PROCEDURE' else "🔧"
        if routine_type == 'FUNCTION':
            try:
                return_type = st.session_state.db_manager._get_function_return_type(specific_name)
                is_refcursor = st.session_state.db_manager._detect_refcursor_return(specific_name)
                if is_refcursor or return_type == 'refcursor':
                    icon = "🔄"
            except:
                pass
        with st.expander(f"{icon} {routine_name} ({routine_type})"):
            parameters = st.session_state.db_manager.get_function_parameters(specific_name)
            input_params = []
            output_params = []
            if parameters:
                for param in parameters:
                    param_name = param['parameter_name']
                    param_type = param['data_type'].upper()
                    param_mode = param['parameter_mode'].upper()
                    if param_mode in ['IN', 'INOUT']:
                        st.markdown(f"**Input Parameter:** `{param_name}` ({param_type})")
                        param_key = f"param_{specific_name}_{param_name}"
                        if param_type in ['INTEGER', 'BIGINT', 'SMALLINT']:
                            param_value = st.number_input(
                                f"{param_name} ({param_type})",
                                key=param_key,
                                step=1,
                                format="%d"
                            )
                        elif param_type in ['NUMERIC', 'DECIMAL', 'FLOAT', 'REAL', 'DOUBLE PRECISION']:
                            param_value = st.number_input(
                                f"{param_name} ({param_type})",
                                key=param_key,
                                step=0.01,
                                format="%.2f"
                            )
                        elif param_type in ['BOOLEAN']:
                            param_value = st.checkbox(
                                f"{param_name} ({param_type})",
                                key=param_key
                            )
                        elif param_type in ['DATE']:
                            param_value = st.date_input(
                                f"{param_name} ({param_type})",
                                key=param_key
                            )
                        elif param_type in ['TIMESTAMP', 'TIMESTAMPTZ']:
                            param_value = st.datetime_input(
                                f"{param_name} ({param_type})",
                                key=param_key
                            )
                        else:
                            param_value = st.text_input(
                                f"{param_name} ({param_type})",
                                key=param_key
                            )
                        input_params.append(param_value)
                    if param_mode in ['OUT', 'INOUT', 'RETURN']:
                        output_params.append(f"`{param_name}` ({param_type}) [{param_mode}]")
                if output_params:
                    st.markdown("**🔁 Output Parameters:**")
                    for out in output_params:
                        st.markdown(f"- {out}")
            button_label = f"🚀 Run {routine_name}"
            if routine_type == 'FUNCTION':
                try:
                    return_type = st.session_state.db_manager._get_function_return_type(specific_name)
                    is_refcursor = st.session_state.db_manager._detect_refcursor_return(specific_name)
                    if is_refcursor or return_type == 'refcursor':
                        button_label = f"🔄 Execute {routine_name} (REF CURSOR)"
                        set_refcursor_FLAG(True)
                except:
                    pass
            if st.button(button_label, key=f"run_{specific_name}"):
                with st.spinner(f"Running {routine_type.lower()} {routine_name}..."):
                    required_inputs = [p for p in parameters if p["parameter_mode"].upper() in ["IN", "INOUT"]]
                    if parameters and len(input_params) != len(required_inputs):
                        st.error(f"❌ Please provide all input parameters for {routine_name}.")
                    else:
                        result, notices = st.session_state.db_manager.execute_routine(
                            routine_name, routine_type, specific_name, input_params, refcursor_FLAG
                        )
                        if notices:
                            st.info("📢 **Database Notices:**")
                            for notice in notices:
                                if notice and notice.strip():
                                    st.markdown(f"- {notice}")
                            st.markdown("---")
                        if routine_type == 'PROCEDURE':
                            if result.empty:
                                st.success(f"✅ Procedure {routine_name} executed successfully")
                            else:
                                st.success(f"✅ Procedure {routine_name} executed successfully with results")
                                row_height = 55
                                table_height = min(len(result) * row_height, 800)
                                st.dataframe(result, use_container_width=True, height=table_height)
                        elif routine_type == 'FUNCTION':
                            if not result.empty:
                                st.success(f"✅ Function {routine_name} executed successfully")
                                row_height = 55
                                table_height = min(len(result) * row_height, 800)
                                if len(result) > 1:
                                    st.markdown(f"**📊 Returned {len(result)} rows**")
                                elif len(result) == 1:
                                    st.markdown("**📊 Returned 1 row**")
                                st.dataframe(result, use_container_width=True, height=table_height)
                                st.markdown("<br>", unsafe_allow_html=True)
                                csv = result.to_csv(index=False)
                                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                filename = f"{routine_name}_result_{timestamp}.csv"
                                col1, col2 = st.columns([1, 3])
                                with col1:
                                    st.download_button(
                                        label="📥 Download CSV",
                                        data=csv,
                                        file_name=filename,
                                        mime="text/csv"
                                    )
                                with col2:
                                    st.markdown(f"*File: {filename}*")
                            else:
                                st.success(f"✅ Function {routine_name} executed successfully (no data returned)")
                        else:
                            st.error(f"❌ Error executing {routine_type.lower()} {routine_name}")
    render_back_to_home_button()
    st.markdown('</div>', unsafe_allow_html=True)

def show_database_statistics():
    """Display database statistics"""
    st.markdown('<div class="ltr">', unsafe_allow_html=True)
    st.markdown("### 📊 Database Statistics")
    render_navigation_buttons()
    if not st.session_state.db_manager:
        st.error("❌ No database connection.")
        render_back_to_home_button()
        return
    tables = st.session_state.db_manager.get_table_names()
    if not tables:
        st.info("ℹ️ No tables found.")
        render_back_to_home_button()
        return
    table_stats = []
    total_records = 0
    total_columns = 0
    progress_bar = st.progress(0)
    status_text = st.empty()
    for i, table in enumerate(tables):
        try:
            status_text.text(f"Processing table: {table}")
            progress_bar.progress((i + 1) / len(tables))
            from sqlalchemy import text
            count_query = text(f"SELECT COUNT(*) as count FROM {table}")
            with st.session_state.db_manager.engine.connect() as conn:
                count_result = pd.read_sql(count_query, st.session_state.db_manager.engine)
            record_count = count_result.iloc[0]['count'] if not count_result.empty else 0
            table_info = st.session_state.db_manager.get_table_info(table)
            column_count = len(table_info.get('columns', []))
            table_stats.append({
                'Table': table,
                'Records': record_count,
                'Columns': column_count
            })
            total_records += record_count
            total_columns += column_count
        except Exception as e:
            st.error(f"❌ Error retrieving statistics for table {table}: {str(e)}")
    progress_bar.empty()
    status_text.empty()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📋 Number of Tables", len(tables))
    with col2:
        st.metric("📊 Total Records", f"{total_records:,}")
    with col3:
        st.metric("🔢 Total Columns", total_columns)
    if table_stats:
        st.markdown("### 📈 Breakdown by Table")
        stats_df = pd.DataFrame(table_stats)
        if len(stats_df) > 0:
            st.bar_chart(stats_df.set_index('Table')['Records'])
        st.dataframe(
            stats_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Table": st.column_config.TextColumn("📋 Table"),
                "Records": st.column_config.NumberColumn("📊 Records", format="%d"),
                "Columns": st.column_config.NumberColumn("🔢 Columns", format="%d")
            }
        )
    render_back_to_home_button()
    st.markdown('</div>', unsafe_allow_html=True)

def show_settings():
    """Settings page with working functionality"""
    st.markdown('<div class="ltr">', unsafe_allow_html=True)
    st.markdown("### 🔧 System Settings")
    render_navigation_buttons()
    if 'settings' not in st.session_state:
        st.session_state.settings = {
            'theme': 'Light',
            'default_limit': 500,
            'auto_refresh': False,
            'session_timeout': 60,
            'confirm_delete': True
        }
    st.markdown("#### 🔗 Connection Information")
    if st.session_state.connection_string:
        safe_connection = st.session_state.connection_string
        if '@' in safe_connection:
            parts = safe_connection.split('@')
            if '://' in parts[0]:
                protocol_user = parts[0].split('://')
                if ':' in protocol_user[1]:
                    user_pass = protocol_user[1].split(':')
                    safe_connection = f"{protocol_user[0]}://{user_pass[0]}:***@{parts[1]}"
        st.code(safe_connection)
    else:
        st.info("ℹ️ No active connection")
    st.markdown("#### 🎨 Display Settings")
    col1, col2 = st.columns(2)
    with col1:
        new_theme = st.selectbox(
            "🎨 Theme",
            options=['Light', 'Dark'],
            index=0 if st.session_state.settings['theme'] == 'Light' else 1,
            key="theme_setting"
        )
        st.session_state.settings['theme'] = new_theme
        new_limit = st.number_input(
            "📊 Default Record Limit",
            min_value=10,
            max_value=10000,
            value=st.session_state.settings['default_limit'],
            step=50,
            key="limit_setting"
        )
        st.session_state.settings['default_limit'] = new_limit
    with col2:
        new_auto_refresh = st.checkbox(
            "🔄 Auto Refresh Tables",
            value=st.session_state.settings['auto_refresh'],
            key="auto_refresh_setting"
        )
        st.session_state.settings['auto_refresh'] = new_auto_refresh
        new_confirm_delete = st.checkbox(
            "⚠️ Confirm Before Delete",
            value=st.session_state.settings['confirm_delete'],
            key="confirm_delete_setting"
        )
        st.session_state.settings['confirm_delete'] = new_confirm_delete
    st.markdown("#### ⏱️ Session Settings")
    new_timeout = st.slider(
        "🕐 Session Timeout (minutes)",
        min_value=5,
        max_value=240,
        value=st.session_state.settings['session_timeout'],
        key="timeout_setting"
    )
    st.session_state.settings['session_timeout'] = new_timeout
    if st.session_state.settings['theme'] == 'Dark':
        st.markdown("""
        <style>
        .stApp {
            background-color: #0e1117;
            color: white;
        }
        .main-header {
            color: #fafafa;
        }
        </style>
        """, unsafe_allow_html=True)
    st.markdown("#### 🗄️ Database Operations")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Test Connection", use_container_width=True):
            if st.session_state.db_manager:
                try:
                    tables = st.session_state.db_manager.get_table_names()
                    st.success(f"✅ Connection successful! Found {len(tables)} tables.")
                except Exception as e:
                    st.error(f"❌ Connection failed: {str(e)}")
            else:
                st.error("❌ No database manager available")
    with col2:
        if st.button("📊 Refresh Schema", use_container_width=True):
            if st.session_state.db_manager:
                with st.spinner("Refreshing schema..."):
                    try:
                        tables = st.session_state.db_manager.get_table_names()
                        st.success(f"✅ Schema refreshed! Found {len(tables)} tables.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Schema refresh failed: {str(e)}")
    with col3:
        if st.button("💾 Save Settings", use_container_width=True):
            st.success("✅ Settings saved successfully!")
            st.balloons()
    render_back_to_home_button()
    st.markdown('</div>', unsafe_allow_html=True)

import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
import os
import re
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

def read_sql_file(file_path: str) -> List[Dict[str, str]]:
    """Read SQL file and split into individual queries with full comment name extraction"""
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        st.error(f"❌ File not found: {file_path}")
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        queries = []
        current_query = []
        current_name = None
        in_comment = False
        query_id = 0
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('/*'):
                in_comment = True
                continue
            if line.endswith('*/'):
                in_comment = False
                continue
            if in_comment:
                continue
            if line.startswith('-- Query') or line.startswith('-- Statement'):
                match = re.match(r'-- (?:Query|Statement) \d+:\s*(.*)', line)
                if match:
                    if current_query and current_name:
                        queries.append({
                            'name': current_name,
                            'sql': '\n'.join(current_query).strip().rstrip(';').strip(),
                            'id': query_id
                        })
                        current_query = []
                    query_id += 1
                    current_name = f"Query {query_id}: {match.group(1).strip()}"
                continue
            if line.startswith('--'):
                continue
            if line:
                current_query.append(line)
            if line.endswith(';') and current_query:
                query_text = '\n'.join(current_query).strip().rstrip(';').strip()
                if query_text:
                    if not current_name:
                        query_id += 1
                        current_name = f"Query {query_id}: Unnamed"
                    queries.append({
                        'name': current_name,
                        'sql': query_text,
                        'id': query_id
                    })
                current_query = []
                current_name = None
        if current_query and current_name:
            query_text = '\n'.join(current_query).strip().rstrip(';').strip()
            if query_text:
                if not current_name:
                    query_id += 1
                    current_name = f"Query {query_id}: Unnamed"
                queries.append({
                    'name': current_name,
                    'sql': query_text,
                    'id': query_id
                })
        return queries
    except Exception as e:
        logger.error(f"Error reading SQL file {file_path}: {str(e)}")
        st.error(f"❌ Error reading {file_path}: {str(e)}")
        return []

def show_queries():
    """Display and execute queries from Queries.sql with numbered run buttons"""
    st.markdown('<div class="ltr">', unsafe_allow_html=True)
    st.markdown("### 📋 Queries")
    render_navigation_buttons()
    queries_path = r"\\wsl.localhost\docker-desktop\mnt\docker-desktop-disk\data\docker\volumes\pgadmin_data\_data\storage\e.solomon.co.il_gmail.com\Queries.sql"
    queries = read_sql_file(queries_path)
    if not queries:
        st.error("❌ No queries found or error reading Queries.sql")
        render_back_to_home_button()
        return
    for query in queries:
        with st.expander(f"🔍 {query['name']}"):
            st.code(query['sql'], language='sql')
            if st.button(f"🚀 Run Query {query['id']}", key=f"run_query_{query['id']}"):
                with st.spinner(f"Running query: {query['name']}..."):
                    try:
                        with st.session_state.db_manager.engine.connect() as conn:
                            result = conn.execute(text(query['sql']))
                            conn.commit()
                            rows = result.fetchall()
                            if rows:
                                df = pd.DataFrame(rows, columns=result.keys())
                                st.dataframe(df, use_container_width=True, height=min(len(df) * 35, 400))
                                st.markdown(f"**Found {len(df)} records**")
                                csv = df.to_csv(index=False)
                                st.download_button(
                                    label="📥 Download as CSV",
                                    data=csv,
                                    file_name=f"query_{query['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                    mime="text/csv",
                                    use_container_width=True
                                )
                            else:
                                st.success(f"✅ Query {query['id']} executed successfully (no data returned)")
                    except Exception as e:
                        st.error(f"❌ Error executing Query {query['id']}: {str(e)}")
    render_back_to_home_button()
    st.markdown('</div>', unsafe_allow_html=True)

def show_main_programs():
    """Display and execute main SQL programs with enhanced UI and results display"""
    st.markdown('<div class="ltr">', unsafe_allow_html=True)
    st.markdown("### 📚 Main Programs")
    render_navigation_buttons()

    base_path = r"\\wsl.localhost\docker-desktop\mnt\docker-desktop-disk\data\docker\volumes\pgadmin_data\_data\storage\e.solomon.co.il_gmail.com"
    program_files = ['main_program_1.sql', 'main_program_2.sql']

    for program_file in program_files:
        program_path = os.path.join(base_path, program_file)
        try:
            with open(program_path, 'r', encoding='utf-8') as file:
                sql_content = file.read()
        except Exception as e:
            st.error(f"❌ Error reading {program_file}: {str(e)}")
            continue

        if not sql_content.strip():
            st.error(f"❌ {program_file} is empty")
            continue

        program_name = os.path.splitext(program_file)[0]
        with st.expander(f"📖 {program_name}", expanded=False):
            st.markdown(f"**Program: {program_name}**")
            st.code(sql_content, language='sql')
            if st.button(f"🚀 Run", key=f"run_program_{program_file}"):
                execute_sql_program(program_name, sql_content)


    render_back_to_home_button()
    st.markdown('</div>', unsafe_allow_html=True)


def execute_sql_program(program_name: str, sql_content: str):
    """Execute SQL program and display results with notices"""
    with st.spinner(f"Running {program_name}..."):
        try:
            # Create raw psycopg2 connection for NOTICE support
            raw_conn = st.session_state.db_manager.engine.raw_connection()
            raw_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

            try:
                with raw_conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Execute the SQL content
                    cursor.execute(sql_content)

                    # Capture notices
                    notices = []
                    if hasattr(raw_conn, 'notices') and raw_conn.notices:
                        notices = [notice.message.strip() if hasattr(notice, 'message') else str(notice).strip()
                                   for notice in raw_conn.notices]

                    # Try to fetch results if available
                    results_data = []
                    try:
                        # Check if there are results to fetch
                        if cursor.description:
                            results = cursor.fetchall()
                            if results:
                                # Convert to list of dictionaries for DataFrame
                                results_data = [dict(row) for row in results]
                    except Exception as fetch_error:
                        # Some queries don't return results (like procedures)
                        st.info(f"ℹ️ No results to fetch: {str(fetch_error)}")

                    # Display results
                    display_execution_results(program_name, results_data, notices)

            finally:
                raw_conn.close()

        except Exception as e:
            st.error(f"❌ Error executing {program_name}: {str(e)}")
            st.exception(e)  # Show full traceback for debugging


def display_execution_results(program_name: str, results_data: list, notices: list):
    """Display execution results including data and notices"""

    # Show success message
    st.success(f"✅ {program_name} executed successfully!")

    # Display notices if any
    if notices:
        st.markdown("### 📢 Notices:")
        for i, notice in enumerate(notices, 1):
            if notice.strip():  # Only show non-empty notices
                st.info(f"**Notice {i}: ** {notice}")

    # Display data results if any
    if results_data:
        st.markdown("### 📊 Results:")
        try:
            df = pd.DataFrame(results_data)

            # Display basic info about the results
            st.markdown(f"**Rows returned:** {len(df)}")
            if not df.empty:
                st.markdown(f"**Columns:** {', '.join(df.columns.tolist())}")

            # Display the data
            if len(df) > 0:
                # Show first few rows in a nice format
                st.dataframe(df, use_container_width=True)

                # Option to download results as CSV
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv,
                    file_name=f"{program_name}_results.csv",
                    mime="text/csv"
                )
            else:
                st.info("No data rows returned")

        except Exception as df_error:
            st.warning(f"Could not format results as DataFrame: {str(df_error)}")
            # Show raw results
            st.json(results_data)
    else:
        st.info("ℹ️ No data results returned (this is normal for procedures that only perform operations)")