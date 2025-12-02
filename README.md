# Project

## 1. Project Overview
This project utilizes a microservices architecture containerized with Docker.

### Service Architecture
| Service | Port 
| :--- | :--- |
| **Frontend** | `3000` |
| **Backend** | `8000` |
| **Database** | `5432` |

---

## 2. Prerequisites
Ensure you have [Docker Desktop](https://www.docker.com/products/docker-desktop/) installled

---

## 3. Quick Start

### Starting the Application
You can run the application in two modes:

**Option A: Standard Mode (Logs in Terminal)**
Use this to see live logs from all containers in your current terminal window.
```bash
docker compose up --build
```

**Option B: Detached Mode (Background)**
Use this if you want to keep using your current terminal window.
```bash
docker compose up --build -d
```

### Stopping the Application
To stop the containers and remove the created networks:
```bash
docker compose down
```

---

## 4. Accessing the Application
Once the containers are running, you can access the services via your browser:

* **Frontend UI:** [http://localhost:3000](http://localhost:3000)
* **Backend API:** [http://localhost:8000/api/data](http://localhost:8000/api/data)

---

## 5. Development Workflow

### Adding New Libraries

If you add a new package to requirements.txt (frontend or backend), you must rebuild the container for it to take effect

```
docker compose up --build
```

### View Logs
If you're running in detached mode you can view the logs like this:
```bash
docker logs -f <container_name_or_id>
```

### Notes

You should install this extention for VS Code it makes managing containers easier and you can see which are running. 

**[Docker for VS Code](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker)**

From time to time you can run the following to command to clean disk space
```
docker system prune -a
```
