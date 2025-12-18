# ParkEasy - Parking Finder Application

A web application to find the nearest available parking houses in Dortmund, Germany. The application provides walking distance and time estimates to help users find convenient parking.

## Prerequisites
Ensure you have [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed

## How to run 
You can run the application in two modes:

**Option A: With Logs in Terminal**

```bash
docker compose up --build
```

**Option B: Detached Mode (Background)**
```bash
docker compose up --build -d
```

### Stopping the Application
```bash
docker compose down
```

## Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000


