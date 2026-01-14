# dto.py
from dataclasses import dataclass
from typing import List

@dataclass
class ParkingRequestDtoNearby:
    lat: float
    lon: float
    ev_charging: str = "false"
    limit: int = 5

    def to_query_params(self) -> dict:
        return {
            "lat": self.lat,
            "lon": self.lon,
            "Ev_charging": self.ev_charging,
            "limit": self.limit
        }


@dataclass
class ParkingRecommendationDtoNearby:
    name: str
    fullAddress: str
    latitude: float
    longitude: float
    capacity: int
    evCharging: bool
    pricePerHour: float
    drivingTimeMinutes: float
    drivingDistanceInKm: float
