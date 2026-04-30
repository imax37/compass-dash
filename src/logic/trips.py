import datetime as dt
import pandas as pd
from datetime import time

def ShiftsToTrips(df, buffer):
    "Convert a shifts schedule to the implied commute schedule"
    trips = df.copy()

    if not pd.api.types.is_datetime64_any_dtype(trips['start_time']):
        raise TypeError("start_time must be datetime64")

    trips['home'] = trips['start_time'] - pd.Timedelta(minutes=buffer)
    trips['YVR'] = trips['end_time']

    trips = trips.melt(id_vars=['date','month','is_weekend'],
                        value_vars=['home','YVR'],
                        var_name='origin',
                        value_name='depart')
    
    return trips.sort_values('date')

def GetOneZoneTrips(df):
    "Find all trips that occur on a weekend or after 6:30pm"
    one_zone = df.loc[(df['is_weekend'] == True) | (df['depart'].dt.time > time(18, 30))]

    return one_zone

def GetTwoZoneTrips(df):
    "find all trips that occur on a weekday before 6:30pm"
    two_zone = df.loc[(df['is_weekend'] == False) & (df['depart'].dt.time < time(18, 30))]

    return two_zone

def GetAddFareTrips(df):
    "find all trips that will incur the YVR add fare"
    add_fare = df.loc[df['origin'] == 'YVR']

    return add_fare

def count_trip_types(trips):
    return{
        "one_zone": GetOneZoneTrips(trips).shape[0],
        "two_zone": GetTwoZoneTrips(trips).shape[0],
        "add_fare": GetAddFareTrips(trips).shape[0]
    }