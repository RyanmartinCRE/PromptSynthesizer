
import streamlit as st

def init_session_state():
    if 'user' not in st.session_state:
        st.session_state['user'] = None
    if "selected_template" not in st.session_state:
        st.session_state.selected_template = ""
    if 'random_tip' not in st.session_state:
        st.session_state.random_tip = None

def login():
    with st.form("login_form"):
        st.markdown("### 🔐 Login to Continue")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            valid_users = {"demo": "pass123"}
            if username in valid_users and password == valid_users[username]:
                st.session_state['user'] = username
                st.success(f"Welcome, {username}!")
            else:
                st.error("Invalid login. Try 'demo' / 'pass123'")

def logout():
    st.session_state['user'] = None
    st.rerun()
