import streamlit as st
from pymongo import MongoClient

st.set_page_config(page_title="Incident Logs", layout="wide")

with st.sidebar:
    if st.button("Logout"):
        st.session_state.clear()
        st.switch_page("Login.py")

if "role" not in st.session_state:
    st.warning("Please login to access this page.")
    st.stop()
st.title("📋 Incident Logs")



MONGO_URI = "mongodb+srv://nshabnam2006:1pZuRuArGzbbNFOm@cluster0.oik5ct5.mongodb.net/"
client = MongoClient(MONGO_URI)
db = client["cat_operator_assistant"]
collection = db["incident_logs"]

incidents = list(collection.find({"predicted_hazard": "Yes"}).sort("logged_at", -1))
if not incidents:
    st.info("No hazard incidents logged yet.")
else:
    for inc in incidents:
        with st.container():
            st.markdown("---")
            st.write(f"**Timestamp:** {inc.get('timestamp', '')}")
            st.write(f"**Machine ID:** {inc.get('machine_id', '')}")
            st.write(f"**Distance to Operator:** {inc.get('distance_to_operator', '')} m")
            st.write(f"**Distance to Machine:** {inc.get('distance_to_machine', '')} m")
            st.write(f"**Machine Status:** {inc.get('machine_status', '')}")
            st.write(f"**Predicted Hazard:** {inc.get('predicted_hazard', '')}")
            st.write(f"*Logged at:* {inc.get('logged_at', '')}")
            st.markdown("---")
