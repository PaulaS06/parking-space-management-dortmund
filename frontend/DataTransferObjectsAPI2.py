# dto.py
from dataclasses import dataclass
from typing import List

@dataclass
class ParkingRequestDtoNearby:
    latitude: float
    longitude: float
    limit: int = 5

    def to_query_params(self) -> dict:
        return {
            "lat": self.latitude,
            "lng": self.longitude,
            "limit": self.limit
        }


@dataclass
class ParkingRecommendationDtoNearby:
    name: str
    fullAddress: str
    latitude: float
    longitude: float
    capacity: int
    pricePerHour: float
    evCharging: bool
    drivingTimeMinutes: int
    drivingDistanceInKm: float
