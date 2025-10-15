# Use Python 3.9 as base image
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables - ensure API_KEY is set at runtime
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata
ENV PYTHONUNBUFFERED=1
ENV API_KEY=""  

# Expose the port the app runs on
EXPOSE 8000

# Command to run the FastAPI application. TODO - Update with timeout and other settings as later
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
