import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import joblib

st.set_page_config(page_title="Operator Dashboard", layout="wide")

with st.sidebar:
    if st.button("Logout"):
        st.session_state.clear()
        st.switch_page("Login.py")
        
st.title("Operator Task Dashboard")

if "operator_id" not in st.session_state or "name" not in st.session_state:
    st.warning("Please login first.")
    st.stop()

operator_id = st.session_state["operator_id"]
name = st.session_state["name"]


@st.cache_data
def load_data():
    return pd.read_csv("backend/machine_log_with_weather_soil.csv")

@st.cache_resource
def load_model():
    return joblib.load("backend/final_task_time_estimator.pkl")

data = load_data()
model = load_model()

def get_features_for_task(task_type):
    if task_type == 'Excavation':
        features = data[data['Load Cycles'] > 5].mean(numeric_only=True).to_dict()
    elif task_type == 'Loading':
        features = data[data['Fuel Used (L)'] > 4].mean(numeric_only=True).to_dict()
    elif task_type == 'Transport':
        features = data[data['Engine Hours'] > 1525].mean(numeric_only=True).to_dict()
    elif task_type == 'Grading':
        features = data[data['Idling Time (min)'] > 30].mean(numeric_only=True).to_dict()
    else:  
        features = data[data['Efficiency Score'] > 1].mean(numeric_only=True).to_dict()
    
    features = {k: (v if pd.notnull(v) else 0) for k, v in features.items()}
    soil_counts = data['Soil Type'].value_counts(normalize=True).to_dict()
    features['Soil Type_Loam'] = soil_counts.get('Loam', 0)
    features['Soil Type_Peat'] = soil_counts.get('Peat', 0)
    features['Soil Type_Sandy'] = soil_counts.get('Sandy', 0)
    features['Soil Type_Silt'] = soil_counts.get('Silt', 0)
    return features

model_features = ['Engine Hours', 'Fuel Used (L)', 'Load Cycles', 'Idling Time (min)',
                  'Efficiency Score', 'Idle Ratio', 'Safety Score', 'Temperature (C)',
                  'Rainfall (mm)', 'Soil Type_Loam', 'Soil Type_Peat', 
                  'Soil Type_Sandy', 'Soil Type_Silt']

response = requests.get(f"http://localhost:8000/tasks/{operator_id}")
tasks = pd.DataFrame(response.json())

st.subheader(f"Operator: {operator_id} | Name: {name}")

if tasks.empty:
    st.info("No tasks assigned yet.")
    st.stop()

if "task_status" not in st.session_state:
    st.session_state["task_status"] = {
        row['task_id']: row["status"] == "completed" for idx, row in tasks.iterrows()
    }


completed_tasks = sum(st.session_state["task_status"].values())
total_tasks = len(tasks)
progress = completed_tasks / total_tasks if total_tasks else 0

st.progress(progress, text=f"{completed_tasks}/{total_tasks} tasks completed")
fig = px.pie(
    names=["Completed", "Remaining"],
    values=[completed_tasks, total_tasks - completed_tasks],
    color_discrete_sequence=["green", "red"],
    hole=0.4
)
st.plotly_chart(fig, use_container_width=True)
st.divider()

for idx, row in tasks.iterrows():
    task_id = row['task_id']
    task_type = row['task_type']
    current_checked = st.session_state["task_status"].get(task_id, row["status"] == "completed")

    col1, col2, col3, col4, col5 = st.columns([2, 3, 3, 3, 2])

    features = get_features_for_task(task_type)
    X_input = pd.DataFrame([features])[model_features]
    predicted_time = model.predict(X_input)[0]

    new_checked = st.checkbox("Completed", key=task_id, value=current_checked)
    if new_checked != current_checked:
        new_status = "completed" if new_checked else "scheduled"
        response = requests.patch(
            f"http://localhost:8000/update_task_status/{task_id}",
            json={"status": new_status},
            headers={"Content-Type": "application/json"}
        )
        print(response.status_code, response.text)
        st.session_state["task_status"][task_id] = new_checked
        st.rerun()

    with col1:
        status_text = "Completed" if new_checked else "Not Completed"
        status_color = "green" if new_checked else "orange"
        st.markdown(f"<span style='color:{status_color}'><b>{status_text}</b></span>", unsafe_allow_html=True)
    with col2:
        st.write(f"Deadline: {row['deadline']}")
    with col3:
        st.write(f"Type: {task_type}")
    with col4:
        st.write(f"Predicted: {predicted_time:.2f} hrs")

st.divider()
