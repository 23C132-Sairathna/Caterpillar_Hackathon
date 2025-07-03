import streamlit as st
import pandas as pd
import joblib
st.set_page_config(page_title="Task Time Estimator", layout="wide")
with st.sidebar:
    if st.button("Logout"):
        st.session_state.clear()
        st.switch_page("Login.py")

if "role" not in st.session_state or st.session_state["role"] not in ["manager", "operator"]:
    st.warning("Please login first.")
    st.stop()

@st.cache_data
def load_data():
    data = pd.read_csv("backend/machine_log_with_weather_soil.csv")
    return data

@st.cache_resource
def load_model():
    return joblib.load("backend/final_task_time_estimator.pkl")


data = load_data()
model = load_model()


st.title("Task Time Estimator Report")


task_types = ['Excavation', 'Loading', 'Transport', 'Grading', 'Hauling']
task_type = st.selectbox("Select Task Type:", task_types)


typical_features_per_task = {
    'Excavation':   data.mean(numeric_only=True).to_dict(),
    'Loading':      data.mean(numeric_only=True).to_dict(),
    'Transport':    data.mean(numeric_only=True).to_dict(),
    'Grading':      data.mean(numeric_only=True).to_dict(),
    'Hauling':      data.mean(numeric_only=True).to_dict(),
}

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


model_features = ['Engine Hours', 'Fuel Used (L)', 'Load Cycles', 'Idling Time (min)',
                  'Efficiency Score', 'Idle Ratio', 'Safety Score', 'Temperature (C)',
                  'Rainfall (mm)', 'Soil Type_Loam', 'Soil Type_Peat', 'Soil Type_Sandy', 'Soil Type_Silt']


soil_counts = data['Soil Type'].value_counts(normalize=True).to_dict()
features['Soil Type_Loam'] = soil_counts.get('Loam', 0)
features['Soil Type_Peat'] = soil_counts.get('Peat', 0)
features['Soil Type_Sandy'] = soil_counts.get('Sandy', 0)
features['Soil Type_Silt'] = soil_counts.get('Silt', 0)


X_input = pd.DataFrame([features])[model_features]


if st.button("Predict Time"):
    predicted_time = model.predict(X_input)[0]
    st.subheader("Estimated Time for Task")
    st.success(f"Estimated time to complete **{task_type}**: **{predicted_time:.2f} hours**")

    with st.expander("See details of average features used"):
        st.write(X_input.T.rename(columns={0: "Value"}))
