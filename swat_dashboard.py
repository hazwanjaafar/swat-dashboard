import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. App Configuration ---
st.set_page_config(page_title="SWaT Dataset Visualizer", layout="wide")
st.title("🌊 SWaT Industrial Control System Dashboard")
st.markdown("Visualizing Cyber-Physical System (CPS) states and sensor correlations.")

# --- 2. Data Ingestion ---
@st.cache_data
def load_data(file_obj):
    # Load dataset; note: SWaT often has leading/trailing spaces in headers
    df = pd.read_csv(file_obj)
    df.columns = df.columns.str.strip()
    # Convert Timestamp to datetime if not already
    if 'Timestamp' in df.columns:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    return df

# UPLOADER: For user to drop the SWaT CSV file
uploaded_file = st.sidebar.file_uploader("Upload SWaT CSV File", type=["csv"])

if uploaded_file:
    df = load_data(uploaded_file)
    
    # --- 3. Sidebar Filters ---
    st.sidebar.header("Visualization Settings")
    
    # Select Time Range (To avoid lag with huge datasets)
    num_rows = st.sidebar.slider("Number of Rows to Display", 100, 10000, 2000)
    display_df = df.head(num_rows)
    
    # Select Stage to Focus On
    stage = st.sidebar.selectbox("Select Plant Stage", ["Stage 1: Intake", "Stage 2: Pre-Treatment"])

    # --- 4. Logic & Visualization ---
    
    if stage == "Stage 1: Intake":
        st.subheader("Stage 1: Tank Levels vs. Pump States")
        
        # Create Subplots: Top for Continuous Sensors, Bottom for Discrete Actuators
        fig = make_subplots(rows=2, cols=1, 
                            shared_xaxes=True, 
                            vertical_spacing=0.1,
                            subplot_titles=("Level (LIT101) & Flow (FIT101)", "Pumps (P101, P102) & Valve (MV101)"))

        # Sensor: LIT101 (Level)
        fig.add_trace(go.Scatter(x=display_df['Timestamp'], y=display_df['LIT101'], 
                                 name="Tank Level (LIT101)", line=dict(color='royalblue')), row=1, col=1)
        
        # Sensor: FIT101 (Flow)
        fig.add_trace(go.Scatter(x=display_df['Timestamp'], y=display_df['FIT101'], 
                                 name="Flow Rate (FIT101)", line=dict(color='cyan')), row=1, col=1)

        # Actuator: P101 (Pump) - Binary State (0 or 1/2)
        fig.add_trace(go.Scatter(x=display_df['Timestamp'], y=display_df['P101'], 
                                 name="Pump P101", line=dict(shape='hv', color='orange')), row=2, col=1)
        
        # Actuator: MV101 (Motorized Valve)
        fig.add_trace(go.Scatter(x=display_df['Timestamp'], y=display_df['MV101'], 
                                 name="Valve MV101", line=dict(shape='hv', color='red')), row=2, col=1)

    elif stage == "Stage 2: Pre-Treatment":
        st.subheader("Stage 2: Chemical Analyzers (pH, Conductivity, ORP)")
        
        fig = go.Figure()
        # Adding chemical sensors
        for sensor_id in ['AIT201', 'AIT202', 'AIT203']:
            fig.add_trace(go.Scatter(x=display_df['Timestamp'], y=display_df[sensor_id], name=sensor_id))

    # General Layout Updates
    fig.update_layout(height=700, template="plotly_dark", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    # --- 5. Data Summary Table ---
    with st.expander("View Raw Data Snippet"):
        st.dataframe(display_df.describe())

else:
    st.info("Please upload the SWaT dataset CSV file in the sidebar to begin.")
    st.image("https://itrust.sutd.edu.sg/wp-content/uploads/sites/3/2016/06/SWaT_Testbed.png", caption="SWaT Testbed Overview")
