FROM python:3.12-slim

# Keep Python output unbuffered and skip .pyc files in the image.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install dependencies first to leverage Docker layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source.
COPY . .

EXPOSE 8000

# mem0's Chroma store persists to ./db (mounted as a volume in compose).
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
