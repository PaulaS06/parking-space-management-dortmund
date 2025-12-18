# backend_rest_client.py
import requests
from typing import List
from DataTransferObjects import ParkingRequestDto, ParkingRecommendationDto

class BackendRestClient:

    def __init__(self, base_url: str, username: str = None, password: str = None, timeout: int = 5):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.auth = (username, password) if username and password else None  # Basic Auth

    def get_parking_recommendations(
        self,
        request: ParkingRequestDto
    ) -> List[ParkingRecommendationDto]:

        url = f"{self.base_url}/api/v1/parkinghouses/walking"

        response = requests.get(
            url,
            params=request.to_query_params(),
            auth=self.auth,
            timeout=self.timeout
        )

        response.raise_for_status()

        return [
            ParkingRecommendationDto(**item)
            for item in response.json()
        ]
