import pandas as pd

def add_datetime_columns(df, start_year = 2026):
    df = df.copy()
    dates = df['date'].to_list()

    parsedDates = []
    currentYear = start_year
    prevMonth = None

    for d in dates:
        dt = pd.to_datetime(d, format="%d-%b")
        month = dt.month

        if prevMonth == 12 and month == 1:
            currentYear += 1

        parsedDates.append(dt.replace(year=currentYear))
        prevMonth = month

    df["date"] = parsedDates
    return df

def parse_times(df):
    df = df.copy()

    df['start_time'] = pd.to_datetime(
        df['date'].dt.strftime("%Y-%m-%d") + " " + df['start_time'],
        format="%Y-%m-%d %H%M"
    )

    df['end_time'] = pd.to_datetime(
        df['date'].dt.strftime("%Y-%m-%d") + " " + df['end_time'],
        format="%Y-%m-%d %H%M"
    )

    return df