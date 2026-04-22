def cost_stored_value(counts: dict, fares: dict) -> float:
    return (
        counts["one_zone"] * fares["1zone"] +
        counts["two_zone"] * fares["2zone"] +
        counts["add_fare"] * fares["yvraddfare"]
    )


def cost_one_zone_pass(counts: dict, fares: dict) -> float:
    return (
        fares["1zonemonth"] +
        counts["two_zone"] * fares["2zoneaddfare"]
    )


def cost_two_zone_pass(counts: dict, fares: dict) -> float:
    return fares["2zonemonth"]

PAYMENT_METHODS = {"One Zone": cost_one_zone_pass,
                    "Two Zone": cost_two_zone_pass,
                     "Stored Value": cost_stored_value}