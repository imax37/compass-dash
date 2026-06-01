import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st
import pandas as pd
from src.parser.orchestrator import parse_pdf
from src.processing.datetime_utils import add_datetime_columns, parse_times
from src.pipeline import run_pipeline
from src.logic.costs import total_costs
from src.config.fare_prices import FARES

st.set_page_config(page_title="Transit Cost Optimizer", layout="wide")

st.title("Transit Cost Optimzer")
st.write("Compare compass card expenses based on your work schedule")

# --- Shift Data Input ---

st.sidebar.header("Input")

demo = st.sidebar.checkbox("Use sample data")

uploaded_files = st.sidebar.file_uploader('Upload one or more schedule PDFs',
                                         accept_multiple_files=True)

if not uploaded_files and not demo:
    st.sidebar.info('Upload a PDF to display input options')

if uploaded_files:
    first = st.sidebar.text_input('Your first name', value='Ian')
    last = st.sidebar.text_input('Your last name', value='Maccarthy')
    month = st.sidebar.selectbox('Select the month you would like to filter',
                             ("January", "February", "March", "April", "May", "June", "July",
                                "August", "September", "October", "November", "December"))
    current_year = st.sidebar.selectbox('Select the year your schedule starts in', (2026, 2025))
    buffer = st.sidebar.slider('Adjust your commute time (minutes)', 30, 120, 60)

if demo:
    first = 'Ian'
    last = 'MacCarthy'
    month = 'March'
    current_year = 2026
    buffer = 60

def load_sample_data():
    raw =  pd.DataFrame({
        "date": pd.date_range("2026-03-01", periods=5, freq="D"),
        "type": ["AGT1"] * 5,
        "start_time": ['1445', '1945', '1445', '1445', '1445'],
        "end_time": ['1845', '2345', '1845', '1845', '1845'],
        "month": ["March"] * 5,
        "is_weekend": [True, False, False, False, False]
    })

    df = parse_times(raw)
    
    return df

# --- ETL AND DISPLAY ---

@st.cache_data
def load_schedules(files, year, first_name, last_name):
    dfs = []
    for file in files:
        df = run_pipeline(file, year, first_name, last_name)
        dfs.append(df)

    combined = pd.concat(dfs, ignore_index=True)

    combined = combined.drop_duplicates(subset=['date','start_time','end_time'])

    return combined

def filter_month(df, month_name):
    return df[df["month"] == month_name]

if demo:
    st.warning("Using Sample Data")
    shift_df = load_sample_data()

elif uploaded_files:
    if not month:
        st.warning('Please select a month')
        st.stop()
    try:
        with st.spinner("Processing schedules..."):
            raw_shifts = load_schedules(uploaded_files, current_year, first, last)
    except Exception as e:
        st.error(f"Failed to parse PDF: {e}")
        st.stop()

    if month not in raw_shifts['month'].values:
        st.error(f"{month} not found in your schedule")
        st.stop()

    try:
        shift_df = filter_month(raw_shifts, month)
    except Exception as e:
        st.error(f"Failed to filter for month {month}: {e}")
        st.stop()

    if shift_df.empty:
        st.error("No shifts found — check name or PDF format")
        st.stop()

else:
    st.info("Upload a PDF to begin, or select sample data")
    st.stop()

st.subheader(f"{month} Shifts for {first.capitalize()} {last.capitalize()}")
st.dataframe(shift_df[["date","type","start_time","end_time"]].style.format({'date':"{:%Y-%B-%d}",
                                                                             'start_time':"{:%H:%M}",
                                                                             "end_time":"{:%H:%M}"}))

# --- Cost Logic ---

@st.cache_data
def compute_costs(df, buffer):
    return total_costs(df, FARES, buffer)

try:
    results = compute_costs(shift_df, buffer)
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
    st.bar_chart(costs_df.sort_values("cost")['cost'])
    st.caption("Inclodes YVR addfare and zone-based pricing.")
    st.caption("Single tickets are YVR addfare exempt.")

with col2:
    st.metric("Cheapest option", best)
    st.metric("Cost", f"${costs_df.loc[best, 'cost']:.2f}")

    baseline = costs_df["cost"].min()
    display_df = costs_df.copy()
    display_df['Savings'] = display_df["cost"] - baseline
    st.subheader("Savings vs best option")
    st.dataframe(display_df.style.format({'cost':"${:.2f}",'Savings':"${:.2f}"}))

st.download_button(
    "Download Results",
    data=costs_df.to_csv(),
    file_name="commute_costs.csv"   
)

st.success(f"best option: {best}")

# --- PASS BENEFIT LOGIC ---

st.subheader('Compass Pass Upgrade Options')

if best == 'Two Zone Pass':
    st.success('Upgraded compass product is already your cheapest option!')

elif best == 'One Zone Pass':
    free_2_zone_trips = abs(costs_df['cost'].loc['Two Zone Pass'] - costs_df['cost'].loc['One Zone Pass']) // FARES.two_zone_add
    st.metric('One zone pass -> Two zone pass', f'{round(free_2_zone_trips, ndigits=None)} trips')
    st.caption('Extra two-zone trips included for free if you use a two zone instead of one zone pass')
    if free_2_zone_trips < 3:
        st.success('Recommended upgrade: Two Zone Pass')

else:
    col1, col2 = st.columns(2)

    if best == 'Single Tickets':
        free_bus_trips = abs(costs_df['cost'].loc['One Zone Pass'] - costs_df['cost'].loc['Single Tickets']) // FARES.one_zone
        col1.metric('Single Tickets -> One zone pass', f'{round(free_bus_trips, ndigits=None)} trips')
        col1.caption('Extra bus trips included for free if you use a one zone pass instead of single tickets')
        if free_bus_trips < 7:
            st.success('Recommended upgrade: One Zone Pass')

    if best == 'Stored Value': # I don't think this is possible, but just in case
        free_bus_trips = abs(costs_df['cost'].loc['One Zone Pass'] - costs_df['cost'].loc['Stored Value']) // FARES.one_zone
        col1.metric('Stored Value -> One zone pass', f'{round(free_bus_trips, ndigits=None)} trips')
        col1.caption('Extra bus trips included for free if you use a one zone pass instead of stored value')
        if free_bus_trips < 9:
            st.success('Recommended upgrade: One Zone Pass')

    free_2_zone_trips = abs(costs_df['cost'].loc['Two Zone Pass'] - costs_df['cost'].loc['One Zone Pass']) // FARES.two_zone_add
    col2.metric('One Zone Pass -> Two Zone Pass', f'{round(free_2_zone_trips, ndigits=None)} trips')
    col2.caption('Extra two-zone trips included for free if you use a two zone instead of one zone pass')

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







