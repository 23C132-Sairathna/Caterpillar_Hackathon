import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pymongo import MongoClient
import datetime

st.set_page_config(page_title="Proximity Hazard Detection", layout="wide")

with st.sidebar:
    if st.button("Logout"):
        st.session_state.clear()
        st.switch_page("Login.py")
        
if "role" not in st.session_state:
    st.warning("Please login to access this page.")
    st.stop()

st.title("Proximity Hazard Detection")
st.write("Provide live input or upload CSV file to detect proximity hazards.")

# MongoDB setup
MONGO_URI = "mongodb+srv://nshabnam2006:1pZuRuArGzbbNFOm@cluster0.oik5ct5.mongodb.net/"
client = MongoClient(MONGO_URI)
db = client["cat_operator_assistant"]
collection = db["incident_logs"]

input_mode = st.radio("Choose Input Mode", ["Manual Input", "Upload CSV File"])

def check_proximity(row):
    operator_threshold = 1.0
    machine_threshold = 2.0
    if row["Machine_Status"] == "Moving":
        if row["Distance_to_Operator"] < operator_threshold or row["Distance_to_Machine"] < machine_threshold:
            return "Yes"
    return "No"

if input_mode == "Manual Input":
    st.subheader("Manual Data Entry")
    timestamp = st.text_input("Timestamp", value=str(datetime.datetime.now()))
    machine_id = st.text_input("Machine ID", value="MCH001")
    distance_to_operator = st.number_input("Distance to Operator (m)", min_value=0.0)
    distance_to_machine = st.number_input("Distance to Machine (m)", min_value=0.0)
    machine_status = st.selectbox("Machine Status", ["Idle", "Moving"])

    if st.button("Check Hazard"):
        hazard = check_proximity({
            "Distance_to_Operator": distance_to_operator,
            "Distance_to_Machine": distance_to_machine,
            "Machine_Status": machine_status
        })
        st.write(f"### Predicted Hazard: {hazard}")
        if hazard == "Yes":
            incident = {
                "timestamp": timestamp,
                "machine_id": machine_id,
                "distance_to_operator": distance_to_operator,
                "distance_to_machine": distance_to_machine,
                "machine_status": machine_status,
                "predicted_hazard": hazard,
                "logged_at": datetime.datetime.now()
            }
            collection.insert_one(incident)
            st.success("Hazard detected and logged to MongoDB.")

else:
    uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.subheader("Raw Data")
        st.dataframe(df)

        df["Predicted_Hazard"] = df.apply(check_proximity, axis=1)
        st.subheader("Prediction Results")
        st.dataframe(df)

        fig, ax = plt.subplots()
        sns.countplot(data=df, x="Predicted_Hazard", palette="Set2", ax=ax)
        ax.set_title("Hazard Prediction Count")
        st.pyplot(fig)

        danger_data = df[df["Predicted_Hazard"] == "Yes"]
        for _, row in danger_data.iterrows():
            incident = {
                "timestamp": row["Timestamp"],
                "machine_id": row["Machine_ID"],
                "distance_to_operator": row["Distance_to_Operator"],
                "distance_to_machine": row["Distance_to_Machine"],
                "machine_status": row["Machine_Status"],
                "predicted_hazard": row["Predicted_Hazard"],
                "logged_at": datetime.datetime.now()
            }
            collection.insert_one(incident)
        st.success(f"{len(danger_data)} hazard records uploaded to MongoDB!")
