# dto.py
from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class ParkingRequestDto:
    latitude: float
    longitude: float
    start_time: datetime
    end_time: datetime
    limit: int = 5

    def to_query_params(self) -> dict:
        return {
            "lat": self.latitude,
            "lng": self.longitude,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "limit": self.limit
        }


@dataclass
class ParkingRecommendationDto:
    name: str
    fullAddress: str
    latitude: float
    longitude: float
    capacity: int
    priceTotal: float
    evCharging: bool
    walkingTimeMinutes: int
    walkingDistanceInKm: float
