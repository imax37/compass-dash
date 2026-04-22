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

def GetOneZoneTrips(df):
    "Find all trips that occur on a weekend or after 6:30pm"
    one_zone = df.loc[(df['is_weekend']==True) | (df['time']>1830)]

    return one_zone

def GetTwoZoneTrips(df):
    "find all trips that occur on a weekday before 6:30pm"
    two_zone = df.loc[(df['is_weekend']==False) & (df['time']<1830)]

    return two_zone

def GetAddFareTrips(df):
    "find all trips that will incur the YVR add fare"
    add_fare = df.loc[df['origin'] == 'YVR']

    return add_fare