FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set Python environment
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip first
RUN pip install --upgrade pip setuptools wheel

# Copy requirements
COPY requirements.txt .

# Install all dependencies including alembic
RUN pip install --no-cache-dir -r requirements.txt

# Verify installations
RUN pip list | grep -i alembic
RUN pip list | grep -i sqlalchemy
RUN pip show alembic

# Test alembic import
RUN python -c "import alembic; print(f'Alembic location: {alembic.__file__}')"
RUN python -c "from alembic.config import main; print('Alembic config import OK')"

# Copy application code
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY scripts/ ./scripts/
COPY alembic.ini .

# Expose port
EXPOSE 8000

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--loop", "asyncio"]
