def validate_data(df):
    if df['date'].isna().any():
        raise ValueError("Missing dates detected")
    
    if df['time'].isna().any():
        raise ValueError("Missing time values detected")
    
    return df

def standardize_columns(df):
    df = df.copy()

    df.columns = [col.strip().lower() for col in df.columns]

    return df

def split_time_column(df):
    df = df.copy()

    times = df['time'].str.split('-', expand=True)
    df['start_time'] = times[0]
    df['end_time'] = times[1]
    #df = df.drop(columns=['time'])

    return df

def clean_time_format(df):
    df = df.copy()

    df['start_time'] = df['start_time'].str.strip()
    df['end_time'] = df['end_time'].str.strip()

    return df

def clean_dataframe(df):
    df = validate_data(df)
    df = standardize_columns(df)
    df = split_time_column(df)
    df = clean_time_format(df)

    return df