# backend/Dockerfile
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install system dependencies (optional)
RUN apt-get update && apt-get install -y gcc

# Copy code
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend app
COPY backend .

# Start FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]