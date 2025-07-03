import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import joblib

st.set_page_config(page_title="Manager Dashboard", layout="wide")

with st.sidebar:
    if st.button("Logout"):
        st.session_state.clear()
        st.switch_page("Login.py")
        
st.title("Manager Fleet Task Dashboard")

if "manager_id" not in st.session_state or "name" not in st.session_state:
    st.warning("Please login first.")
    st.stop()

manager_id = st.session_state["manager_id"]
name = st.session_state["name"]

st.subheader(f"Manager: {manager_id} | Name: {name}")

if st.button("Refresh Data from Server"):
    st.rerun()


response = requests.get("http://localhost:8000/all_tasks")
tasks = pd.DataFrame(response.json())

if tasks.empty:
    st.info("No tasks available.")
    st.stop()

total_tasks = len(tasks)
completed_tasks = (tasks["status"] == "completed").sum()
pending_tasks = (tasks["status"] != "completed").sum()

col1, col2, col3 = st.columns(3)
col1.metric("Total Tasks", total_tasks)
col2.metric("Completed Tasks", completed_tasks)
col3.metric("Pending Tasks", pending_tasks)

st.divider()

st.subheader("Operator Task Progress")
for operator_id, group in tasks.groupby("operator_id"):
    total = len(group)
    done = (group["status"] == "completed").sum()
    progress = done / total if total else 0
    st.write(f"**Operator {operator_id}:** {done}/{total} tasks completed")
    st.progress(progress)

st.divider()


st.subheader("Task Type Completion Across All Operators")
task_type_summary = tasks.groupby("task_type")["status"].apply(
    lambda x: (x == "completed").sum() / len(x)
).reset_index().rename(columns={"status": "completion_rate"})

fig2 = px.bar(
    task_type_summary,
    x="task_type",
    y="completion_rate",
    text=task_type_summary["completion_rate"].apply(lambda x: f"{x:.0%}"),
    color="completion_rate",
    color_continuous_scale="blues",
    labels={"task_type": "Task Type", "completion_rate": "Completion %"},
    title="Task Type Completion Rate"
)
fig2.update_yaxes(range=[0,1])
st.plotly_chart(fig2, use_container_width=True)

st.divider()


st.subheader("Predicted vs Actual Completed Time")


@st.cache_data
def load_data():
    return pd.read_csv("backend/machine_log_with_weather_soil.csv")

@st.cache_resource
def load_model():
    return joblib.load("backend/final_task_time_estimator.pkl")

data = load_data()
model = load_model()

operator_selected = st.selectbox("Select Operator:", tasks["operator_id"].unique(), key="op_select")
task_selected = st.selectbox("Select Task Type:", tasks["task_type"].unique(), key="task_select")

if st.button("Predict for Selected Operator & Task"):
    filtered_tasks = tasks[
        (tasks["operator_id"] == operator_selected) &
        (tasks["task_type"] == task_selected) &
        (tasks["status"] == "completed")
    ]

    if not filtered_tasks.empty:
        actual_avg_time = filtered_tasks["est_time"].mean()
    else:
        actual_avg_time = 0


    if task_selected == 'Excavation':
        features = data[data['Load Cycles'] > 5].mean(numeric_only=True).to_dict()
    elif task_selected == 'Loading':
        features = data[data['Fuel Used (L)'] > 4].mean(numeric_only=True).to_dict()
    elif task_selected == 'Transport':
        features = data[data['Engine Hours'] > 1525].mean(numeric_only=True).to_dict()
    elif task_selected == 'Grading':
        features = data[data['Idling Time (min)'] > 30].mean(numeric_only=True).to_dict()
    else:
        features = data[data['Efficiency Score'] > 1].mean(numeric_only=True).to_dict()

    features = {k: (v if pd.notnull(v) else 0) for k, v in features.items()}
    soil_counts = data['Soil Type'].value_counts(normalize=True).to_dict()
    features['Soil Type_Loam'] = soil_counts.get('Loam', 0)
    features['Soil Type_Peat'] = soil_counts.get('Peat', 0)
    features['Soil Type_Sandy'] = soil_counts.get('Sandy', 0)
    features['Soil Type_Silt'] = soil_counts.get('Silt', 0)

    model_features = ['Engine Hours', 'Fuel Used (L)', 'Load Cycles', 'Idling Time (min)',
                      'Efficiency Score', 'Idle Ratio', 'Safety Score', 'Temperature (C)',
                      'Rainfall (mm)', 'Soil Type_Loam', 'Soil Type_Peat', 'Soil Type_Sandy', 'Soil Type_Silt']
    X_input = pd.DataFrame([features])[model_features]
    predicted_time = model.predict(X_input)[0]

   
    comparison_df = pd.DataFrame({
        "Metric": ["Actual Avg Completed Time", "Predicted Time"],
        "Hours": [actual_avg_time, predicted_time]
    })

    fig3 = px.bar(comparison_df, x="Metric", y="Hours", color="Metric",
                  text=comparison_df["Hours"].apply(lambda x: f"{x:.2f}"),
                  title=f"Predicted vs Actual Time for {task_selected} by {operator_selected}")
    st.plotly_chart(fig3, use_container_width=True)

st.divider()
st.divider()
st.subheader("Assign New Task")

with st.form("assign_task_form"):
    selected_operator = st.selectbox("Select Operator to Assign:", tasks["operator_id"].unique(), key="assign_op")
    task_type = st.selectbox("Select Task Type:", ["Excavation", "Loading", "Transport", "Grading", "Hauling"], key="assign_task")
    deadline = st.date_input("Select Deadline")

    submit_btn = st.form_submit_button("Assign Task")
    if submit_btn:
        payload = {
            "operator_id": selected_operator,
            "task_type": task_type,
            "deadline": str(deadline),
            "status": "scheduled"
        }
        try:
            response = requests.post("http://localhost:8000/add_task", json=payload)
            if response.status_code == 200:
                st.success(f"Task assigned to {selected_operator} successfully!")
                st.rerun()
            else:
                st.error(f"Failed to assign task. Server responded: {response.text}")
        except Exception as e:
            st.error(f"Error connecting to server: {e}")

def highlight_status(val):
    color = "green" if val == "completed" else "orange"
    return f"color: {color}"

st.write("All Tasks By Operator")
for operator_id, group in tasks.groupby("operator_id"):
    st.write(f"Operator {operator_id}")
    st.dataframe(
        group.style.applymap(highlight_status, subset=["status"]),
        use_container_width=True
    )
