from dataclasses import dataclass

def cost_stored_value(counts: dict, FARES: dataclass) -> float:
    return (
        counts["one_zone"] * FARES.one_zone +
        counts["two_zone"] * FARES.two_zone +
        counts["add_fare"] * FARES.yvr_add
    )


def cost_one_zone_pass(counts: dict, FARES: dataclass) -> float:
    return (
        FARES.one_zone_month +
        counts["two_zone"] * FARES.two_zone_add
    )


def cost_two_zone_pass(counts: dict, FARES: dataclass) -> float:
    return FARES.two_zone_month

PAYMENT_METHODS = {"One Zone Pass": cost_one_zone_pass,
                    "Two Zone Pass": cost_two_zone_pass,
                     "Stored Value": cost_stored_value}