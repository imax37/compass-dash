import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st
from src.parser.orchestrator import parse_pdf
from src.pipeline import run_pipeline
from src.logic.costs import total_costs
from src.config.fare_prices import FARES

uploaded_file = st.file_uploader('Upload a Schedule PDF')

if uploaded_file:
    shifts_list = parse_pdf(uploaded_file)
else:
    st.info("Upload a PDF to begin")

st.dataframe(shifts_list)

shift_df = run_pipeline(uploaded_file, start_year=2026)

results = total_costs(shift_df, FARES)
costs_df = results['costs']
counts = results['counts']
trips = results['trips']

st.dataframe(costs_df)

st.bar_chart(costs_df)

best = costs_df['cost'].idxmin()
st.success(f"best option: {best}")
