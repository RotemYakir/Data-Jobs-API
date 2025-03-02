# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.8.19
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing .pyc files and buffering logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Create a non-privileged user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Copy and install dependencies
COPY requirements.txt .
RUN python -m pip install -r requirements.txt --no-cache-dir

COPY data_jobs .

# Switch to non-root user
USER appuser

# Copy the entire project
COPY . .

# Expose Flask API port
EXPOSE 8000

# Run Flask API as a module
CMD ["python", "-m", "data_jobs.main"]