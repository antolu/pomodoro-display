FROM python:3.11-slim

# Set environment variables for production
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FLASK_ENV=production

# Create non-root user for security
RUN groupadd -r pomodoro && useradd -r -g pomodoro pomodoro

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and git metadata for version detection
COPY pomodoro_display/ ./pomodoro_display/
COPY pyproject.toml .
COPY .git/ ./.git/

# Install the application in editable mode
RUN pip install -e .

# Create data directory for persistent config
RUN mkdir -p /app/data && chown pomodoro:pomodoro /app/data

# Switch to non-root user
USER pomodoro

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/status || exit 1

# Set the command to run the application
CMD ["python", "-m", "flask", "--app", "pomodoro_display.app", "run", "--host=0.0.0.0", "--port=5000"]
