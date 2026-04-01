def add_features(df):
    df = df.copy()
    df['weekday'] = df["date"].dt.day_name()
    df["is_weekend"] = df["date"].dt.weekday >=5
    df['month'] = df['date'].dt.month_name()
    return df