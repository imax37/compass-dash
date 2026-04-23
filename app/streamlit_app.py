import streamlit as st
from src.parser.pdf_reader import parse_pdf

uploaded_file = st.file_uploader('upload schedule pdf')

if uploaded_file:
    shifts = parse_pdf(uploaded_file)

st.dataframe(shifts)