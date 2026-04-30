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

def filter_month(df, month_name):
    return df[df["month"] == month_name]

if demo:
    st.warning("Using Sample Data")
    shift_df = load_sample_data()

elif uploaded_file:
    if not month:
        st.warning('Please select a month')
        st.stop()
    try:
        shift_df_unfiltered = load_shifts(uploaded_file)
    except Exception as e:
        st.error(f"Failed to parse PDF: {e}")
        st.stop()

    assert month in shift_df_unfiltered['month'].values, f"{month} not found in your schedule!"

    try:
        shift_df = filter_month(shift_df_unfiltered, month)
    except Exception as e:
        st.error(f"Failed to filter for month {month}: {e}")
        st.stop()

else:
    st.info("Upload a PDF to begin")
    st.stop()

st.subheader(f"Your Shifts for {month}")
st.dataframe(shift_df[["date","type","start_time","end_time"]])

# --- Cost Logic ---

@st.cache_data
def compute_costs(df):
    return total_costs(df, FARES)

try:
    results = compute_costs(shift_df)
except Exception as e:
    st.error(f"Cost calculations failed: {e}")
    st.stop()

costs_df = results['costs']
counts = results['counts']
trips = results['trips']

# --- OUTPUTS ---
st.subheader("Cost Comparison")
best = costs_df['cost'].idxmin()

col1, col2 = st.columns(2)

with col1:
    st.bar_chart(costs_df.sort_values("cost"))
    st.caption("Inclodes YVR addfare and zone-based pricing")

with col2:
    st.metric("Cheapest option", best)
    st.metric("Cost", f"${costs_df.loc[best, 'cost']:.2f}")

    baseline = costs_df["cost"].min()
    costs_df['Savings'] = costs_df["cost"] - baseline
    st.subheader("Savings vs best option")
    st.dataframe(costs_df.style.format({'cost':"${:.2f}",'Savings':"${:.2f}"}))

st.download_button(
    "Download Results",
    data=costs_df.to_csv(),
    file_name="commute_costs.csv"   
)

st.success(f"best option: {best}")

# --- PASS BENEFIT LOGIC ---

st.subheader('Pass Benefit Comparison')

col1, col2 = st.columns(2)

if best == 'Two Zone Pass':
    st.success('Upgraded compass product is already your cheapest option!')

else:

    free_bus_trips = abs(costs_df['cost'].loc['One Zone Pass'] - costs_df['cost'].loc['Stored Value']) // FARES.one_zone

    if best == 'One Zone Pass':
        col1.metric('Stored Value -> One Zone Pass', f'{round(free_bus_trips, ndigits=None)} trips')
        col1.caption('Equivalent bus fares that you save with your one zone pass')

    else:
        col1.metric('One zone pass', f'{round(free_bus_trips, ndigits=None)} trips')
        col1.caption('Extra bus trips included if you use a one zone pass instead of stored value')

    free_2_zone_trips = abs(costs_df['cost'].loc['Two Zone Pass'] - costs_df['cost'].loc['One Zone Pass']) // FARES.two_zone_add
    col2.metric('One Zone -> Two Zone Pass', f'{round(free_2_zone_trips, ndigits=None)} trips')
    col2.caption('Extra two-zone trips included if you use a two zone instead of one zone pass')

# --- TRIP BREAKDOWN ---

st.subheader("Trip Type Breakdown")

col1, col2, col3 = st.columns(3)
col1.metric("1-Zone Trips", counts["one_zone"])
col2.metric("2-Zone Trips", counts["two_zone"])
col3.metric("YVR AddFare Trips", counts["add_fare"])

# --- DATA TABLES ---
with st.expander("Shift Data"):
    st.dataframe(shift_df)

with st.expander("Trip Data"):
    st.dataframe(trips)







