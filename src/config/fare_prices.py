from dataclasses import dataclass

@dataclass(frozen=True)
class FareConfig:
    one_zone: float = 2.70
    two_zone: float = 4.00
    one_zone_month: float = 111.60
    two_zone_month: float = 149.25
    two_zone_add: float = 1.50
    yvr_add: float = 5.00

FARES = FareConfig()