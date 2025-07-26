FROM python:3.12-slim

WORKDIR /app
pip install --upgrade pip

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt