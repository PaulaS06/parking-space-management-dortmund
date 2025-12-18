# ParkEasy - Parking Finder Application

A web application to find the nearest available parking houses in Dortmund, Germany. The application provides walking distance and time estimates to help users find convenient parking.

## Project Structure

```
test-parking/
├── backend/           # Flask REST API backend
│   ├── app.py        # Main API with parking search endpoints
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/          # Flask frontend web UI
│   ├── app.py        # Frontend server
│   ├── templates/    # HTML templates
│   ├── static/       # CSS, JS, and images
│   ├── requirements.txt
│   └── Dockerfile
├── database/          # Database models and setup
│   ├── database.py   # SQLAlchemy models
│   └── create_db.py  # Database initialization
├── data/             # JSON data storage
├── docker-compose.yaml
└── requirements.txt  # Root dependencies
```

## Features

- **Real-time parking availability**: Fetches live data from Dortmund open data API
- **Geocoding support**: Search by address or coordinates
- **Walking distance calculation**: Uses Haversine formula and Geoapify routing API
- **Opening hours validation**: Filters parking by availability during requested time
- **Responsive web interface**: Clean UI with geolocation support

## Prerequisites

- Docker and Docker Compose
- Python 3.9+ (for local development)

## Quick Start with Docker

1. Clone the repository:
   ```bash
   git clone https://github.com/k-lk324/test-parking.git
   cd test-parking
   ```

2. Start the application:
   ```bash
   docker-compose up --build
   ```

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

## Local Development

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python app.py
```

The backend will run on `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
pip install -r requirements.txt
python app.py
```

The frontend will run on `http://localhost:3000`

## API Endpoints

### GET /api/v1/parkinghouses/walking

Find nearest parking houses within walking distance.

**Parameters:**
- `address` (string): Address to search from (optional if lat/lon provided)
- `lat` (float): Latitude coordinate (optional if address provided)
- `lon` (float): Longitude coordinate (optional if address provided)
- `start_time` (ISO 8601 string): Start time for parking
- `end_time` (ISO 8601 string): End time for parking
- `limit` (integer): Number of results to return (default: 5)

**Example:**
```bash
curl "http://localhost:8000/api/v1/parkinghouses/walking?address=Sonnenstrasse%2096,%20Dortmund&start_time=2024-01-15T10:00:00&end_time=2024-01-15T18:00:00&limit=5"
```

**Response:**
```json
[
  {
    "id": "parking_id",
    "name": "Parking House Name",
    "fullAddress": "Full Address",
    "lat": 51.4883,
    "lon": 7.4249,
    "capacity": 500,
    "freeSpots": 123,
    "distance_haversine_km": 0.845,
    "walkingDistanceInKm": 0.912,
    "walkingTimeMinutes": 11.5
  }
]
```

## Configuration

### API Keys

The backend uses Geoapify APIs for geocoding and routing. API keys are included in the code but should be moved to environment variables for production:

- `GEOAPIFY_GEOCODE_KEY`
- `GEOAPIFY_ROUTING_KEY`

### Environment Variables

Set these in docker-compose.yaml or your environment:

- `DATABASE_URL`: Database connection string (default: sqlite:///data/app.db)
- `BACKEND_URL`: Backend API URL for frontend (default: http://backend:8000)
- `DEBUG`: Set to "true" to enable Flask debug mode (default: false, **NOT recommended for production**)

**Security Note**: Debug mode is disabled by default for security. Only enable it in development environments.

## Technologies Used

- **Backend**: Flask, Flask-RESTful, Flask-SQLAlchemy
- **Frontend**: Flask, HTML5, CSS3, JavaScript
- **APIs**: Dortmund Open Data, Geoapify Geocoding & Routing
- **Containerization**: Docker, Docker Compose
- **Database**: SQLite (configurable)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is open source and available under the MIT License.