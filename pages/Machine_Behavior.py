import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt
from pymongo import MongoClient
from datetime import datetime
st.set_page_config(page_title="Machine Behavior Analyzer", layout="wide")

with st.sidebar:
    if st.button("Logout"):
        st.session_state.clear()
        st.switch_page("Login.py")
        
if "role" not in st.session_state:
    st.warning("Please login to access this page.")
    st.stop()

@st.cache_resource
def load_model():
    return joblib.load("backend/unusual_behavior_model.pkl")

model = load_model()


MONGO_URI = "mongodb+srv://nshabnam2006:1pZuRuArGzbbNFOm@cluster0.oik5ct5.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client["cat_operator_assistant"]
incident_collection = db["incident_logs"]


def explain_issues(row):
    reasons = []
    if row["Idling Time (min)"] > 50:
        reasons.append("Excessive Idling")
    if row["Seatbelt Status"] == 1 and row["Safety Alert Triggered"] == 1:
        reasons.append("Unsafe Operation")
    if row["Efficiency Score"] < 1.2:
        reasons.append("Low Fuel Efficiency")
    return ", ".join(reasons) if reasons else "Normal Usage"

def compute_safety_score(row):
    score = 100
    if row["Seatbelt Status"] == 1:  # 1 = Unfastened
        score -= 30
    if row["Safety Alert Triggered"] == 1:  # 1 = Yes
        score -= 20
    if row["Idling Time (min)"] > 40:
        score -= 15
    return max(score, 0)


st.title("Machine Behavior Analyzer")
st.markdown("Detect and explain unusual machine usage based on safety and efficiency patterns.")

option = st.radio("Choose Input Mode:", ["Upload CSV", "Manual Form Input"])

if option == "Upload CSV":
    file = st.file_uploader("Upload CSV file", type="csv")
    if file:
        df = pd.read_csv(file)

        df["Seatbelt Status"] = df["Seatbelt Status"].map({"Fastened": 0, "Unfastened": 1})
        df["Safety Alert Triggered"] = df["Safety Alert Triggered"].map({"No": 0, "Yes": 1})
    else:
        st.stop()

elif option == "Manual Form Input":
    with st.form("manual_input_form"):
        machine_id = st.text_input("Machine ID (e.g., EXC001)")
        fuel = st.number_input("Fuel Used (L)", min_value=0.0)
        load_cycles = st.number_input("Load Cycles", min_value=0)
        idling = st.number_input("Idling Time (min)", min_value=0)
        seatbelt = st.selectbox("Seatbelt Status", ["Fastened", "Unfastened"])
        alert = st.selectbox("Safety Alert Triggered", ["No", "Yes"])
        efficiency = st.number_input("Efficiency Score", min_value=0.0)
        idle_ratio = st.number_input("Idle Ratio", min_value=0.0)
        submitted = st.form_submit_button("Analyze")

    if submitted:
        df = pd.DataFrame([{
            "Machine ID": machine_id,
            "Fuel Used (L)": fuel,
            "Load Cycles": load_cycles,
            "Idling Time (min)": idling,
            "Seatbelt Status": 0 if seatbelt == "Fastened" else 1,
            "Safety Alert Triggered": 0 if alert == "No" else 1,
            "Efficiency Score": efficiency,
            "Idle Ratio": idle_ratio
        }])
    else:
        st.stop()

df["Safety Score"] = df.apply(compute_safety_score, axis=1)

features = [
    "Fuel Used (L)", "Load Cycles", "Idling Time (min)",
    "Seatbelt Status", "Safety Alert Triggered",
    "Efficiency Score", "Idle Ratio", "Safety Score" 
]
df["Predicted Label"] = model.predict(df[features])
df["Behavior Status"] = df["Predicted Label"].map({0: "Normal", 1: "Unusual"})
df["Why"] = df.apply(explain_issues, axis=1)

timestamp_now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
df["Timestamp"] = timestamp_now

st.subheader("📊 Prediction Results")
st.dataframe(df[[
    "Timestamp", "Machine ID", "Fuel Used (L)", "Load Cycles", "Idling Time (min)",
    "Efficiency Score", "Idle Ratio", "Safety Score",
    "Behavior Status", "Why"
]])


for _, row in df.iterrows():
    timestamp_now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    df.loc[df["Machine ID"] == row["Machine ID"], "Timestamp"] = timestamp_now

    if row["Predicted Label"] == 1:
        st.warning(f"⚠️ [Time: {timestamp_now}] Machine {row['Machine ID']} → {row['Behavior Status']} → {row['Why']}")
        incident = {
            "timestamp": datetime.utcnow(),
            "Machine ID": row["Machine ID"],
            "Fuel Used (L)": row["Fuel Used (L)"],
            "Load Cycles": row["Load Cycles"],
            "Idling Time (min)": row["Idling Time (min)"],
            "Efficiency Score": row["Efficiency Score"],
            "Safety Score": row["Safety Score"],
            "Reason": row["Why"]
        }
        incident_collection.insert_one(incident)
    else:
        st.success(f"✅ [Time: {timestamp_now}] Machine {row['Machine ID']} → {row['Behavior Status']}")



status_counts = df["Behavior Status"].value_counts()
fig, ax = plt.subplots()
ax.pie(status_counts, labels=status_counts.index, autopct="%1.1f%%", startangle=90)
ax.axis("equal")
st.subheader("📈 Summary")
st.pyplot(fig)
