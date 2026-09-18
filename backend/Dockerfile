FROM python:3.14-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy project
COPY pyproject.toml .
COPY src ./src

# Install dependencies
RUN uv pip install --python $(which python) .

# Set env vars
ENV PYTHONUNBUFFERED=1 \
    LOG_LEVEL=INFO

# Expose port
EXPOSE 8000

# Start app
CMD ["uvicorn", "nba_ai.main:app", "--host", "0.0.0.0", "--port", "8000"]
