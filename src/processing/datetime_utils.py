import pandas as pd

def add_datetime_columns(df, start_year = 2026):
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
