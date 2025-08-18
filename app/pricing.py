
from dataclasses import dataclass

@dataclass(frozen=True)
class Plan:
    code: str
    name: str
    devices_min: int
    devices_max: int
    monthly_price: float

def get_plans(settings):
    return [
        Plan("T2",  "Up to 2 devices", 1, 2,  settings.price_t2),
        Plan("T5",  "3–5 devices",     3, 5,  settings.price_t5),
        Plan("T7",  "5–7 devices",     5, 7,  settings.price_t7),
        Plan("T10", "7–10 devices",    7, 10, settings.price_t10),
    ]
