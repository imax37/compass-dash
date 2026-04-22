from .trips import ShiftsToTrips, count_trip_types
from .fares import PAYMENT_METHODS

def total_costs(shifts, fares):

    trips = ShiftsToTrips(shifts)
    counts = count_trip_types(trips)

    costs = {
        name: fn(counts, fares)
        for name, fn in PAYMENT_METHODS.items()
    }

    # return as a dataframe (flipped) along with all the nice intermediate data
    return {
        "costs": pd.DataFrame.from_dict(costs, orient='index', columns=['cost']),
        "counts": counts,
        "trips": trips
    }