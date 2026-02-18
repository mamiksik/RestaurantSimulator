# Use Python 3.14 slim image as base
FROM python:3.14-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install uv for faster Python package management
RUN pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml uv.lock* ./

# Install Python dependencies using uv
RUN uv pip install --system -r pyproject.toml

# Copy project
COPY . .

# Create a non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
