# backend_rest_client.py
import requests
from Exceptions import BackendServerError, InvalidParameterError, NoResultsError, AuthFailedError
from typing import List
from DataTransferObjects import ParkingRequestDto, ParkingRecommendationDto

class BackendRestClient:

    def __init__(self, base_url: str, api_key: str, timeout: int = 5):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.api_key = api_key

    def get_parking_recommendations(
        self,
        request: ParkingRequestDto
    ) -> List[ParkingRecommendationDto]:

        url = f"{self.base_url}/api/v1/parkinghouses/walking"

        try:
            response = requests.get(
                url,
                params=request.to_query_params(),
                headers={"X-API-Key": self.api_key},
                timeout=self.timeout
            )
        except requests.RequestException as e:
            raise BackendServerError(f"Backend not reachable: {e}")

        if response.status_code == 400:
            raise InvalidParameterError("Invalid or missing request parameters")

        if response.status_code == 401:
            raise AuthFailedError("Authentication failed")

        if response.status_code == 404:
            raise NoResultsError("No parking garages found")

        if response.status_code >= 500:
            raise BackendServerError("Backend internal server error")

        return [
            ParkingRecommendationDto(**item)
            for item in response.json()
        ]
