import pandas as pd
from src.parser.orchestrator import parse_pdf
from src.processing.cleaning import clean_dataframe
from src.processing.datetime_utils import add_datetime_columns, parse_times
from src.processing.features import add_features

def run_pipeline(pdf_path, start_year, first_name, last_name):
    if not first_name or not last_name:
        raise ValueError('Employee first and last name must be provided')
    raw_data = parse_pdf(pdf_path, first_name, last_name)

    df = pd.DataFrame(raw_data)
    df = clean_dataframe(df)
    df = add_datetime_columns(df, start_year)
    df = parse_times(df)
    df = add_features(df)

    return df