# Use a slim Python base image for a smaller container
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements and install dependencies first for faster layer caching
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY ./app /app/app

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run the application using Uvicorn
# 'app.main:app' refers to the 'app' object in the 'main.py' file inside the 'app' package
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]