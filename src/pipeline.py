import pandas as pd
from src.parser.orchestrator import parse_pdf
from src.processing.cleaning import clean_dataframe
from src.processing.datetime_utils import add_datetime_columns
from src.processing.features import add_features

def run_pipeline(pdf_path, start_year):
    raw_data = parse_pdf(pdf_path)

    df = pd.DataFrame(raw_data)
    df = clean_dataframe(df)
    df = add_datetime_columns(df, start_year)
    df = add_features(df)

    return df