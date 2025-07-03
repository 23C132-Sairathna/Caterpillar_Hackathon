import streamlit as st
import requests

st.set_page_config(
    page_title="Login",
    page_icon="",
    layout="centered"
)
with st.sidebar:
    if st.button("Logout"):
        st.session_state.clear()
        st.switch_page("Login.py")
st.title("Caterpillar Task Dashboard Login")
st.subheader("Login")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    if not username or not password:
        st.warning("Please enter both username and password.")
    else:
        try:
            response = requests.post(
                "http://localhost:8000/login",
                params={"username": username, "password": password},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                st.session_state["name"] = data["name"]
                if data["role"] == "operator":
                    st.session_state["role"] = "operator"
                    st.session_state["operator_id"] = data["operator_id"]
                    st.success("Login successful! Redirecting to Operator View...")
                    st.switch_page("pages/1_Operator_View.py")
                elif data["role"] == "manager":
                    st.session_state["role"] = "manager"
                    st.session_state["manager_id"] = data["manager_id"]
                    st.success("Login successful! Redirecting to Manager View...")
                    st.switch_page("pages/2_Manager_View.py")
            else:
                st.error("Invalid username or password.")
        except requests.exceptions.RequestException:
            st.error("Unable to connect to backend. Please check your server.")

st.divider()
