def ShiftsToTrips(df):
    "Convert a shifts schedule to the implied commute schedule"
    trips = df.copy()

    #Commute assumption: leave 1h before shift
    trips['home'] = trips['start_time'].astype(int) - 100
    trips['YVR'] = trips['end_time'].astype(int)

    trips = trips.melt(id_vars=['date','month','is_weekend'],
                        value_vars=['home','YVR'],
                        var_name='origin',
                        value_name='time')
    
    return trips.sort_values('date')