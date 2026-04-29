import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st
import pandas as pd
from src.parser.orchestrator import parse_pdf
from src.pipeline import run_pipeline
from src.logic.costs import total_costs
from src.config.fare_prices import FARES

st.set_page_config(page_title="Transit Cost Optimizer", layout="wide")

st.title("Transit Cost Optimzer")
st.write("Compare compass card expenses based on your work schedule")

# --- Shift Data Input ---

st.sidebar.header("Input")

uploaded_file = st.sidebar.file_uploader('Upload a Schedule PDF')
demo = st.sidebar.checkbox("Use sample data")
st.sidebar.warning("The following controls are inactive")
buffer = st.sidebar.slider("Commute time (minutes)", 30, 120, 60)
month = st.sidebar.selectbox("Month",("February", "March", "April"), placeholder="Select a month to compare")


def load_sample_data():
    return pd.DataFrame({
        "date": pd.date_range("2026-03-01", periods=5, freq="D"),
        "type": ["AGT1"] * 5,
        "start_time": [1445, 1445, 1445, 1445, 1445],
        "end_time": [1845, 1845, 1845, 1845, 1845],
        "month": ["March"] * 5,
        "is_weekend": [True, False, False, False, False]
    })

# --- ETL AND DISPLAY ---

@st.cache_data
def load_shifts(file):
    return run_pipeline(file, start_year=2026)

if uploaded_file:
    try:
        shift_df = load_shifts(uploaded_file)
    except Exception as e:
        st.error(f"Failed to parse PDF: {e}")

elif demo:
    st.warning("Using Sample Data")
    shift_df = load_sample_data()

else:
    st.info("Upload a PDF to begin")
    st.stop()
    

st.dataframe(shift_df[["date","type","start_time","end_time"]])

# --- Cost Logic ---

@st.cache_data
def compute_costs(df):
    return total_costs(df, FARES)

try:
    results = compute_costs(shift_df)
except Exception as e:
    st.error(f"Cost calculations failed: {e}")

costs_df = results['costs']
counts = results['counts']
trips = results['trips']

# --- OUTPUTS ---
st.subheader("Cost Comparison")
best = costs_df['cost'].idxmin()
st.success(f"best option: {best}")

col1, col2 = st.columns(2)

with col1:
    st.bar_chart(costs_df.sort_values("cost"))
    st.caption("Inclodes YVR addfare and zone-based pricing")

with col2:
    st.metric("Best Option", best)
    st.metric("Cost", f"${costs_df.loc[best, 'cost']:.2f}")

    baseline = costs_df["cost"].min()
    costs_df['Savings'] = costs_df["cost"] - baseline
    st.subheader("Savings vs best option")
    st.dataframe(costs_df.style.format({'cost':"${:.2f}", 'Savings':"${:.2f}"}))

st.download_button(
    "Download Results",
    data=costs_df.to_csv(),
    file_name="commute_costs.csv"   
)


# --- TRIP BREAKDOWN ---

st.subheader("📊 Trip Breakdown")

col1, col2, col3 = st.columns(3)
col1.metric("1-Zone Trips", counts["one_zone"])
col2.metric("2-Zone Trips", counts["two_zone"])
col3.metric("YVR AddFare Trips", counts["add_fare"])

# --- DATA TABLES ---
with st.expander("Shift Data"):
    st.dataframe(shift_df)

with st.expander("Trip Data"):
    st.dataframe(trips)







